package org.apache.commons.numbers.examples.jmh.complex.generated;
import java.util.concurrent.atomic.AtomicIntegerFieldUpdater;
public class SinCosPerformance_jmhType_B2 extends SinCosPerformance_jmhType_B1 {
    public volatile int setupTrialMutex;
    public volatile int tearTrialMutex;
    public final static AtomicIntegerFieldUpdater<SinCosPerformance_jmhType_B2> setupTrialMutexUpdater = AtomicIntegerFieldUpdater.newUpdater(SinCosPerformance_jmhType_B2.class, "setupTrialMutex");
    public final static AtomicIntegerFieldUpdater<SinCosPerformance_jmhType_B2> tearTrialMutexUpdater = AtomicIntegerFieldUpdater.newUpdater(SinCosPerformance_jmhType_B2.class, "tearTrialMutex");

    public volatile int setupIterationMutex;
    public volatile int tearIterationMutex;
    public final static AtomicIntegerFieldUpdater<SinCosPerformance_jmhType_B2> setupIterationMutexUpdater = AtomicIntegerFieldUpdater.newUpdater(SinCosPerformance_jmhType_B2.class, "setupIterationMutex");
    public final static AtomicIntegerFieldUpdater<SinCosPerformance_jmhType_B2> tearIterationMutexUpdater = AtomicIntegerFieldUpdater.newUpdater(SinCosPerformance_jmhType_B2.class, "tearIterationMutex");

    public volatile int setupInvocationMutex;
    public volatile int tearInvocationMutex;
    public final static AtomicIntegerFieldUpdater<SinCosPerformance_jmhType_B2> setupInvocationMutexUpdater = AtomicIntegerFieldUpdater.newUpdater(SinCosPerformance_jmhType_B2.class, "setupInvocationMutex");
    public final static AtomicIntegerFieldUpdater<SinCosPerformance_jmhType_B2> tearInvocationMutexUpdater = AtomicIntegerFieldUpdater.newUpdater(SinCosPerformance_jmhType_B2.class, "tearInvocationMutex");

    public volatile boolean readyTrial;
    public volatile boolean readyIteration;
    public volatile boolean readyInvocation;
}
