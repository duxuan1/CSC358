/* ******************************************************************
RDT network emulator by Jim Kurose, edited by Larry Zhang
used to implement the Stop-and-Wait (SAW) or Go-Back-N (GBN) protocols

   Network properties:
   - one way network delay with an avearge of 5 time units (longer if 
     there are other messages in the channel for GBN), but can be larger
   - packets can be corrupted (either the header or the data portion)
     or lost, according to user-defined probabilities
   - packets will be delivered in the order in which they were sent
     (although some can be lost).
**********************************************************************/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
/* NO OTHER INCLUDE IS ALLOWED */

#define BIDIRECTIONAL 0 /* change to 1 if you're doing bidirectional transfer */
                        /* which requ  ires writing the routine B_send() */

#define MSG_SIZE 20

/* a "msg" is the data unit passed from the application layer (teacher's code)
 * to the transport layer (students' code). It contains the data (characters)
 * to be delivered to the application layer via the students transport level
 * protocol entities.
 *
 * DO NOT MODIFY
 */
struct msg {
    char data[MSG_SIZE];
};

/* a packet is the data unit passed from the transport layer (students code) to
 * the network layer (teachers code). Note the pre-defined packet structure,
 * which all students must follow. 
 *
 * DO NOT MODIFY
 */
struct pkt {
    int seqnum;
    int acknum;
    int checksum;
    char payload[MSG_SIZE];
};

/* 
 * Declarations of the routines (implemented in teacher's code) that students
 * may use. You should NOT call any other routine in teacher's code.
 */
void starttimer(int AorB, float increment);
void stoptimer(int AorB);
void to_network_layer(int AorB, struct pkt packet);
void to_application_layer(int AorB, char datasent[MSG_SIZE]);


/* 
 * TODO: WRITE THE FOLLOWING ROUTINES
 * You may add other functions, struct definitions, enums, if needed.
 *
 * NOTE: Do NOT print any message to stderr in our code, i.e., do not use
 *       fprintf(stderr, ...) in your code.
 * It is OK to use printf() since it prints to stdout.
 */

#define A 0
#define B 1

struct A_side {
    int seq;
    int ack;
    float increment;
    struct pkt prev_pck; // in case a resend needed
} A_side;

struct B_side {
    int seq;
} B_side;

/*
 * compute the checksum for a packet
 */
int get_checksum(struct pkt packet) {
    int checksum = 0;
    checksum += packet.seqnum;
    checksum += packet.acknum;
    for (int i = 0; i < MSG_SIZE; i++)
        checksum += packet.payload[i];
    return checksum;
}

/*
 * check if a packet is corrupted
 * return 0 if not corrupted
 * return 1 if corrupyed
 */
int is_corrupted(struct pkt packet) {
    if (packet.checksum == get_checksum(packet)) {
        return 0;
    }
    return 1;
}

/*
 * check if a packet is corrupted
 * return 0 if not corrupted
 * return 1 if corrupyed
 */
struct pkt make_pkt(struct msg message) {
    struct pkt packet;
    packet.seqnum = A_side.seq;
    packet.acknum = A_side.ack;
    strncpy(packet.payload, message.data, 20);
    packet.checksum = get_checksum(packet);
    return packet;
}

/* 
 * the following routine will be called once (only) before any other
 * entity A routines are called. You can use it to do any initialization 
 */
void A_init(void) {
    A_side.ack = 0;
    A_side.seq = 0;
    A_side.increment = 1000;
}

/* called from the application layer, passed the data to be sent to other side */
void A_send(struct msg message) {
    struct pkt new_packet = make_pkt(message);
    to_network_layer(A, new_packet);
    starttimer(A, A_side.increment);
}

/* called from network layer, when a packet arrives for transport layer */
void A_recv(struct pkt packet) {
    if (is_corrupted(packet) == 1) {
        printf("A_recv: packet corrupted.\n");
        return;
    }
    if (packet.acknum != A_side.seq) {
        printf("A_recv: not the expected ACK.\n");
        return;
    }
    stoptimer(A);
    
}

/* called when A's timer goes off (timeout) */
void A_timeout(void) {
    
}

/* The following routine will be called once (only) before any other entity B
 * routines are called. You can use it to do any initialization */
void B_init(void) {
    
}

/* called from network layer, when a packet arrives for transport layer at B*/
void B_recv(struct pkt packet) {
    
}

/* called from the application layer, passed the data to be sent to other side.
 * need be completed only for bidiretional transfer */
void B_send(struct msg message) {
    /* Only for bidiretional transfer */
    /* Not needed for unidiretional transfer */
}

/* called when B's timer goes off (timeout)
 * need be completed only for bidiretional transfer */
void B_timeout(void) {
    /* Only for bidiretional transfer */
    /* Not needed for unidiretional transfer */
}

/*********** NETWORK EMULATION CODE (TEACHER'S CODE) STARTS BELOW ***********
The code below emulates the network layer and below network environment:
    - emulates the tranmission and delivery (possibly with bit-level corruption
        and packet loss) of packets across the network/transport interface
    - handles the starting/stopping of a timer, and generates timer
        interrupts (resulting in calling students timer handler).
    - generates message to be sent (passed from application to transport layer)

DO NOT MODIFY ANY CODE BELOW. YOU SHOLD NOT TOUCH, OR REFERENCE (in your code)
ANY OF THE DATA STRUCTURES BELOW. However, reading the code below may help you
better understand the simulation.
******************************************************************/

struct event {
    float evtime;       /* event time */
    int evtype;         /* event type code */
    int eventity;       /* entity where event occurs */
    struct pkt *pktptr; /* ptr to packet (if any) assoc w/ this event */
    struct event *prev;
    struct event *next;
};
struct event *evlist = NULL; /* the event list */

/* possible events: */
#define TIMER_INTERRUPT 0
#define FROM_APP_LAYER 1
#define FROM_NET_LAYER 2

#define OFF 0
#define ON 1
#define A 0
#define B 1

int TRACE = 3;     /* for debugging */
int nsim = 0;      /* number of messages from app to transport layer so far */
int nsimmax = 0;   /* number of msgs to generate, then stop */
float time = 0.000;
float lossprob;    /* probability that a packet is dropped  */
float corruptprob; /* probability that one bit is packet is flipped */
float lambda;      /* arrival rate of messages from application layer */
int n_to_network_layer;     /* number sent into network layer */
int nlost;         /* number lost in media */
int ncorrupt;      /* number corrupted by media*/

void init(int argc, char **argv);
void generate_next_arrival(void);
void insertevent(struct event *p);

int main(int argc, char **argv) {
    struct event *eventptr;
    struct msg msg2give;
    struct pkt pkt2give;

    int i, j;
    char c;

    init(argc, argv);
    A_init();
    B_init();

    while (1) {
        eventptr = evlist; /* get next event to simulate */
        if (eventptr == NULL)
            goto terminate;
        evlist = evlist->next; /* remove this event from event list */
        if (evlist != NULL)
            evlist->prev = NULL;
        if (TRACE >= 2) {
            fprintf(stderr, "EVENT time: %f,", eventptr->evtime);
            fprintf(stderr, "  type: %d", eventptr->evtype);
            if (eventptr->evtype == 0)
                fprintf(stderr, ", timerinterrupt  ");
            else if (eventptr->evtype == 1)
                fprintf(stderr, ", from app layer");
            else
                fprintf(stderr, ", from network layer ");
            fprintf(stderr, " entity: %d\n", eventptr->eventity);
        }
        time = eventptr->evtime; /* update time to next event time */
        if (eventptr->evtype == FROM_APP_LAYER) {
            if (nsim < nsimmax) {
                if (nsim + 1 < nsimmax)
                    generate_next_arrival(); /* set up future arrival */
                /* fill in msg to give with string of same letter */
                j = nsim % 26;
                for (i = 0; i < MSG_SIZE; i++)
                    msg2give.data[i] = 97 + j;
                msg2give.data[MSG_SIZE-1] = 0;
                if (TRACE > 2) {
                    fprintf(stderr, "\tMAINLOOP: data given to student: ");
                    for (i = 0; i+1 < MSG_SIZE; i++)
                        fprintf(stderr, "%c", msg2give.data[i]);
                    fprintf(stderr, "\n");
                }
                nsim++;
                if (eventptr->eventity == A)
                    A_send(msg2give);
                else
                    B_send(msg2give);
            }
        } else if (eventptr->evtype == FROM_NET_LAYER) {
            pkt2give.seqnum = eventptr->pktptr->seqnum;
            pkt2give.acknum = eventptr->pktptr->acknum;
            pkt2give.checksum = eventptr->pktptr->checksum;
            for (i = 0; i < MSG_SIZE; i++)
                pkt2give.payload[i] = eventptr->pktptr->payload[i];
            if (eventptr->eventity == A) /* deliver packet by calling */
                A_recv(pkt2give); /* appropriate entity */
            else
                B_recv(pkt2give);
            free(eventptr->pktptr); /* free the memory for packet */
        } else if (eventptr->evtype == TIMER_INTERRUPT) {
            if (eventptr->eventity == A)
                A_timeout();
            else
                B_timeout();
        } else {
            fprintf(stderr, "INTERNAL PANIC: unknown event type \n");
        }
        free(eventptr);
    }

terminate:
    fprintf(stderr, "Terminated at time %f\n after sending %d msgs from app layer\n",
            time, nsim);
}

void init(int argc, char **argv) /* initialize the simulator */
{
    int i;
    float sum, avg;
    float jimsrand();

    if (argc != 5) {
        fprintf(stderr, "usage: %s  num_sim  prob_loss  prob_corrupt  interval\n", 
                argv[0]);
        exit(1);
    }

    nsimmax = atoi(argv[1]);
    lossprob = atof(argv[2]);
    corruptprob = atof(argv[3]);
    lambda = atof(argv[4]);
    fprintf(stderr, "-----  RDT Network Simulator -------- \n\n");
    fprintf(stderr, "the number of messages to simulate: %d\n", nsimmax);
    fprintf(stderr, "packet loss probability: %f\n", lossprob);
    fprintf(stderr, "packet corruption probability: %f\n", corruptprob);
    fprintf(stderr, "average time between messages from sender's app layer: %f\n", 
            lambda);
    fprintf(stderr, "TRACE: %d\n", TRACE);


    srand(9999); /* init random number generator */
    sum = 0.0;   /* test random number generator for students */
    for (i = 0; i < 1000; i++)
        sum = sum + jimsrand(); /* jimsrand() should be uniform in [0,1] */
    avg = sum / 1000.0;
    if (avg < 0.25 || avg > 0.75) {
        fprintf(stderr, "The random number generation on your machine\n");
        fprintf(stderr, "is different from what this emulator expects.\n");
        fprintf(stderr, "Please take a look at the routine jimsrand() \n");
        fprintf(stderr, "in the emulator code\n");
        exit(1);
    }

    n_to_network_layer = 0;
    nlost = 0;
    ncorrupt = 0;

    time = 0.0;              /* initialize time to 0.0 */
    generate_next_arrival(); /* initialize event list */
}

/****************************************************************************/
/* jimsrand(): return a float in range [0,1].  The routine below is used to */
/* isolate all random number generation in one location.  We assume that the*/
/* system-supplied rand() function return an int in therange [0,mmm]        */
/****************************************************************************/
float jimsrand(void) {
    double mmm = RAND_MAX;
    float x;                 /* individual students may need to change mmm */
    x = rand() / mmm;        /* x should be uniform in [0,1] */
    return (x);
}

/********************* EVENT HANDLINE ROUTINES *******/
/*  The next set of routines handle the event list   */
/*****************************************************/

void generate_next_arrival(void) {
    double x, log(), ceil();
    struct event *evptr;
    float ttime;
    int tempint;

    if (TRACE > 2)
        fprintf(stderr, "\tGENERATE NEXT ARRIVAL: creating new arrival\n");

    x = lambda * jimsrand() * 2; /* x is uniform on [0,2*lambda] */
                                                             /* having mean of lambda        */
    evptr = (struct event *)malloc(sizeof(struct event));
    evptr->evtime = time + x;
    evptr->evtype = FROM_APP_LAYER;
    if (BIDIRECTIONAL && (jimsrand() > 0.5))
        evptr->eventity = B;
    else
        evptr->eventity = A;
    insertevent(evptr);
}

void insertevent(struct event *p) {
    struct event *q, *qold;

    if (TRACE > 2) {
        fprintf(stderr, "\tINSERTEVENT: time is %lf\n", time);
        fprintf(stderr, "\tINSERTEVENT: future time will be %lf\n", p->evtime);
    }
    q = evlist;      /* q points to header of list in which p struct inserted */
    if (q == NULL) { /* list is empty */
        evlist = p;
        p->next = NULL;
        p->prev = NULL;
    } else {
        for (qold = q; q != NULL && p->evtime > q->evtime; q = q->next)
            qold = q;
        if (q == NULL) { /* end of list */
            qold->next = p;
            p->prev = qold;
            p->next = NULL;
        } else if (q == evlist) { /* front of list */
            p->next = evlist;
            p->prev = NULL;
            p->next->prev = p;
            evlist = p;
        } else { /* middle of list */
            p->next = q;
            p->prev = q->prev;
            q->prev->next = p;
            q->prev = p;
        }
    }
}

void printevlist(void) {
    struct event *q;
    int i;
    fprintf(stderr, "--------------\nEvent List Follows:\n");
    for (q = evlist; q != NULL; q = q->next) {
        fprintf(stderr, "Event time: %f, type: %d entity: %d\n", 
                q->evtime, q->evtype, q->eventity);
    }
    fprintf(stderr, "--------------\n");
}

/********************** Student-callable ROUTINES ***********************/

/* called by students routine to cancel a previously-started timer */
void stoptimer(int AorB) {
    struct event *q, *qold;

    if (TRACE > 2)
        fprintf(stderr, "\tSTOP TIMER: stopping timer at %f\n", time);
    /* for (q=evlist; q!=NULL && q->next!=NULL; q = q->next)  */
    for (q = evlist; q != NULL; q = q->next)
        if ((q->evtype == TIMER_INTERRUPT && q->eventity == AorB)) {
            /* remove this event */
            if (q->next == NULL && q->prev == NULL)
                evlist = NULL;        /* remove first and only event on list */
            else if (q->next == NULL) /* end of list - there is one in front */
                q->prev->next = NULL;
            else if (q == evlist) { /* front of list - there must be event after */
                q->next->prev = NULL;
                evlist = q->next;
            } else { /* middle of list */
                q->next->prev = q->prev;
                q->prev->next = q->next;
            }
            free(q);
            return;
        }
    fprintf(stderr, "Warning: unable to cancel your timer. It wasn't running.\n");
}

void starttimer(int AorB, float increment) {
    struct event *q;
    struct event *evptr;

    if (TRACE > 2)
        fprintf(stderr, "\tSTART TIMER: starting timer at %f\n", time);
    /* be nice: check to see if timer is already started, if so, then  warn */
    /* for (q=evlist; q!=NULL && q->next!=NULL; q = q->next)  */
    for (q = evlist; q != NULL; q = q->next)
        if ((q->evtype == TIMER_INTERRUPT && q->eventity == AorB)) {
            fprintf(stderr, "Warning: starting a timer that is already started\n");
            return;
        }

    /* create future event for when timer goes off */
    evptr = (struct event *)malloc(sizeof(struct event));
    evptr->evtime = time + increment;
    evptr->evtype = TIMER_INTERRUPT;
    evptr->eventity = AorB;
    insertevent(evptr);
}

/************************** TO_NETWORK_LAYER ***************/
/* A or B is trying to stop timer */
void to_network_layer(int AorB , struct pkt packet) {
    struct pkt *mypktptr;
    struct event *evptr, *q;
    float lastime, x;
    int i;

    n_to_network_layer++;

    /* simulate losses: */
    if (jimsrand() < lossprob) {
        nlost++;
        if (TRACE > 0)
            fprintf(stderr, "\tTO_NETWORK_LAYER: packet being lost\n");
        return;
    }
    fprintf(stderr, "\tTO_NETWORK_LAYER: packet not lost\n");

    /* make a copy of the packet student just gave me since they may decide */
    /* to do something with the packet after we return back to them */
    mypktptr = (struct pkt *)malloc(sizeof(struct pkt));
    mypktptr->seqnum = packet.seqnum;
    mypktptr->acknum = packet.acknum;
    mypktptr->checksum = packet.checksum;
    for (i = 0; i < MSG_SIZE; i++)
        mypktptr->payload[i] = packet.payload[i];

    /* create future event for arrival of packet at the other side */
    evptr = (struct event *)malloc(sizeof(struct event));
    evptr->evtype = FROM_NET_LAYER; /* packet will pop out from netowrk layer*/
    evptr->eventity = (AorB + 1) % 2; /* event occurs at other entity */
    evptr->pktptr = mypktptr;         /* save ptr to my copy of packet */
    /* finally, compute the arrival time of packet at the other end.
       medium can not reorder, so make sure packet arrives between 1 and 10
       time units after the latest arrival time of packets
       currently in the medium on their way to the destination */
    lastime = time;
    /* for (q=evlist; q!=NULL && q->next!=NULL; q = q->next) */
    for (q = evlist; q != NULL; q = q->next)
        if ((q->evtype == FROM_NET_LAYER && q->eventity == evptr->eventity))
            lastime = q->evtime;
    evptr->evtime = lastime + 1 + 9 * jimsrand();

    /* simulate corruption: */
    if (jimsrand() < corruptprob) {
        ncorrupt++;
        if ((x = jimsrand()) < .75)
            mypktptr->payload[0] = 'Z'; /* corrupt payload */
        else if (x < .875)
            mypktptr->seqnum = 999999;
        else
            mypktptr->acknum = 999999;
        if (TRACE > 0)
            fprintf(stderr, "\tTO_NETWORK_LAYER: packet being corrupted\n");
    }
    if (TRACE > 2)
        fprintf(stderr, "\tTO_NETWORK_LAYER: scheduling arrival on other side\n");
    insertevent(evptr);
}

void to_application_layer(int AorB, char datasent[MSG_SIZE]) {
    int i;
    if (TRACE > 2) {
        fprintf(stderr, "\tTO_APP_LAYER: data received: ");
        for (i = 0; i+1 < MSG_SIZE; i++)
            fprintf(stderr, "%c", datasent[i]);
        fprintf(stderr, "\n");
    }
}

