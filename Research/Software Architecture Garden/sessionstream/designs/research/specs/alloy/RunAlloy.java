import edu.mit.csail.sdg.alloy4.A4Reporter;
import edu.mit.csail.sdg.ast.Command;
import edu.mit.csail.sdg.ast.Module;
import edu.mit.csail.sdg.parser.CompUtil;
import edu.mit.csail.sdg.translator.A4Options;
import edu.mit.csail.sdg.translator.A4Solution;
import edu.mit.csail.sdg.translator.TranslateAlloyToKodkod;

/**
 * Minimal headless Alloy 6 runner: compiles a .als file and executes every
 * command, printing SAT/UNSAT per command. A satisfiable "check" command
 * means a counterexample exists (the assertion is violated).
 */
public final class RunAlloy {
    public static void main(String[] args) throws Exception {
        if (args.length < 1) {
            System.err.println("usage: RunAlloy <file.als> [commandLabelPrefix]");
            System.exit(2);
        }
        String filter = args.length > 1 ? args[1] : null;
        // Silence kodkod's java.util.logging INFO spam.
        java.util.logging.Logger root = java.util.logging.Logger.getLogger("");
        root.setLevel(java.util.logging.Level.OFF);
        for (java.util.logging.Handler h : root.getHandlers()) {
            h.setLevel(java.util.logging.Level.OFF);
        }
        A4Reporter rep = new A4Reporter();
        Module world = CompUtil.parseEverything_fromFile(rep, null, args[0]);
        A4Options opt = new A4Options(); // default solver: bundled SAT4J
        for (Command cmd : world.getAllCommands()) {
            if (filter != null && !cmd.label.startsWith(filter)) {
                continue;
            }
            long t0 = System.nanoTime();
            A4Solution sol = TranslateAlloyToKodkod.execute_command(
                    rep, world.getAllReachableSigs(), cmd, opt);
            long ms = (System.nanoTime() - t0) / 1_000_000;
            boolean sat = sol.satisfiable();
            String outcome;
            if (cmd.check) {
                outcome = sat ? "COUNTEREXAMPLE (assertion violated)"
                              : "NO COUNTEREXAMPLE (holds within scope)";
            } else {
                outcome = sat ? "SAT (instance found)" : "UNSAT (no instance)";
            }
            System.out.printf("%-5s %-24s %s [%d ms]%n", cmd.check ? "check" : "run",
                    cmd.label, outcome, ms);
            System.out.flush();
        }
    }
}
