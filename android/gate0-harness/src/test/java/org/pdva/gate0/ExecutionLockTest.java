package org.pdva.gate0;

import java.lang.reflect.Modifier;

/** Runs the actual management entry point on a desktop JVM with SDK stubs.
 * No Android implementation, test doubles, native library or device is executed.
 */
public final class ExecutionLockTest {
    public static void main(String[] args) {
        for (var constructor : Session.class.getDeclaredConstructors()) {
            if (!Modifier.isPrivate(constructor.getModifiers()))
                throw new AssertionError("Session construction exposed");
        }
        try {
            if (!Modifier.isPrivate(Session.class.getDeclaredMethod("run", boolean.class).getModifiers()))
                throw new AssertionError("Instance execution exposed");
        } catch (ReflectiveOperationException failure) { throw new AssertionError(failure); }
        for (int repeat = 0; repeat < 100; repeat++) {
            for (boolean death : new boolean[] {false, true}) {
                try {
                    // A null context and throwing SDK stubs are tripwires: denial must precede
                    // construction, Android access, reservation, allocation and delegation.
                    Session.run(null, death);
                    throw new AssertionError("execution returned without denial");
                } catch (SecurityException denied) {
                    if (!"research_execution_disabled".equals(denied.getMessage()))
                        throw new AssertionError("wrong denial", denied);
                } catch (Throwable failure) {
                    throw new AssertionError("execution lock failed before Android access", failure);
                }
            }
        }
        try {
            // Read-only observation of the actual reservation guard, not a replacement oracle.
            var guard = Session.class.getDeclaredField("ATTEMPT");
            guard.setAccessible(true);
            var attempted = ResearchAttempt.class.getDeclaredField("attempted");
            attempted.setAccessible(true);
            if (attempted.getBoolean(guard.get(null)))
                throw new AssertionError("denial consumed reservation state");
        } catch (ReflectiveOperationException failure) { throw new AssertionError(failure); }
        System.out.println("PASS: 200 management entry denials before Android access");
    }
}
