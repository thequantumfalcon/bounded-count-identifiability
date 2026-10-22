(* Read-only theorem/theory audit.
   API signatures checked against extracted Isabelle2025-2 sources; see the
   separate api-source-check.json receipt. This file does not construct theorems.
   The caller supplies exact (fully-qualified name, theorem) pairs.
*)
structure Count_Endpoint_Audit =
struct

fun require b message = if b then () else error ("ENDPOINT_AUDIT: " ^ message);

val expected_definitions =
 [("Count_Endpoints.pair_box_def_raw",
   @{prop "Count_Endpoints.pair_box \<equiv>
      (\<lambda>B a c d e p b.
        0 \<le> p \<and> p \<le> 1 \<and> 0 \<le> b \<and> b \<le> B \<and>
        a \<le> p+b \<and> p+b \<le> c \<and>
        d \<le> b^2+2*p*b \<and> b^2+2*p*b \<le> e)"}),
  ("Count_Endpoints.feasible_def_raw",
   @{prop "Count_Endpoints.feasible \<equiv>
      (\<lambda>B a c d e p. \<exists>b. Count_Endpoints.pair_box B a c d e p b)"})];

fun run ctxt labelled_roots =
  let
    val thy = Proof_Context.theory_of ctxt;
    val _ = require (not (Config.get ctxt Goal.quick_and_dirty))
      "quick_and_dirty is enabled in audit context";
    val baseline = @{theory Complex_Main};
    val base_axioms = Theory.all_axioms_of baseline;
    val target_axioms = Theory.all_axioms_of thy;
    val base_names = map #1 base_axioms;
    val delta = filter (fn (name, _) => not (member (op =) base_names name)) target_axioms;
    val expected_names = map #1 expected_definitions;
    val root_names = map #1 labelled_roots;
    val registered_roots = map (fn (name, supplied) =>
      let
        val actual = Global_Theory.get_thm thy name;
        val _ = require (Thm.prop_of actual aconv Thm.prop_of supplied)
          ("label and supplied theorem disagree: " ^ name);
      in (name, actual) end) labelled_roots;
    val roots = map #2 registered_roots;
    val _ = require (not (null roots)) "empty root inventory";
    val _ = require (length (distinct (op =) root_names) = length root_names)
      "duplicate root name";
    val _ = List.app (fn (name, prop) =>
      (writeln ("ENDPOINT_AUDIT_AXIOM " ^ name);
       writeln (Syntax.string_of_term ctxt prop))) delta;
    val _ = require (sort_strings (map #1 delta) = sort_strings expected_names)
      (cat_lines (["unexpected local axiom inventory"] @
        map (fn (name, _) => "ACTUAL_AXIOM " ^ name) delta @
        map (fn name => "EXPECTED_AXIOM " ^ name) expected_names));
    val _ = List.app (fn (name, prop) =>
      let
        val expected = the (AList.lookup (op =) expected_definitions name);
        (* Isabelle stores the existential predicate in eta-contracted form.
           Compare complete typed terms in beta/eta normal form; no definitions,
           arithmetic identities, assumptions, or theorems are rewritten. *)
        val actual_normal = Envir.beta_eta_contract prop;
        val expected_normal = Envir.beta_eta_contract expected;
      in
        if actual_normal aconv expected_normal then ()
        else error ("ENDPOINT_AUDIT: local defining equation differs from independent specification: " ^ name ^
          "\nACTUAL_TERM " ^ ML_Syntax.print_term prop ^
          "\nEXPECTED_TERM " ^ ML_Syntax.print_term expected ^
          "\nBETA_ETA_ALPHA_EQUAL " ^ Bool.toString
            (Envir.beta_eta_contract prop aconv Envir.beta_eta_contract expected))
      end) delta;
    val _ = List.app (fn (name, prop) =>
      (case AList.lookup (op =) target_axioms name of
        SOME actual => require (actual aconv prop) ("imported axiom changed: " ^ name)
      | NONE => error ("ENDPOINT_AUDIT: imported axiom disappeared: " ^ name))) base_axioms;
    val _ = List.app (fn (name, thm) =>
      (require (null (Thm.hyps_of thm)) ("hidden local hypotheses in " ^ name);
       require (null (Thm.tpairs_of thm)) ("unresolved term constraints in " ^ name);
       writeln ("ENDPOINT_AUDIT_ROOT " ^ name);
       writeln (Syntax.string_of_term ctxt (Thm.prop_of thm)))) registered_roots;
    val oracles = Thm_Deps.all_oracles roots;
    val _ = Pretty.writeln (Thm_Deps.pretty_thm_oracles ctxt roots);
    val _ = require (not (Thm_Deps.has_skip_proof roots)) "skip_proof dependency";
    val _ = require (null oracles) "nonempty transitive oracle dependencies";
    val summary = "ENDPOINT_AUDIT_PASS roots=" ^ string_of_int (length roots) ^
      " local_definitions=" ^ string_of_int (length delta) ^ " oracles=0";
    (* Retain rendered proposition text, without Isabelle IDE markup attributes
       that may contain local source paths. Logical terms are not transformed. *)
    fun display_prop prop = XML.content_of (YXML.parse_body (Syntax.string_of_term ctxt prop));
    val report = cat_lines
      (["ENDPOINT_AUDIT_REPORT_V1", "BASELINE Complex_Main",
        "QUICK_AND_DIRTY false", "DEFINITION_COMPARISON typed_beta_eta_alpha",
        "LOCAL_AXIOMS " ^ string_of_int (length delta)] @
       maps (fn (name, prop) =>
         ["ENDPOINT_AUDIT_AXIOM " ^ name,
          "PROPOSITION " ^ display_prop prop,
          "TYPED_TERM " ^ ML_Syntax.print_term prop]) delta @
       maps (fn (name, thm) =>
         ["ENDPOINT_AUDIT_ROOT " ^ name,
          "PROPOSITION " ^ display_prop (Thm.prop_of thm),
          "TYPED_TERM " ^ ML_Syntax.print_term (Thm.prop_of thm),
          "HYPOTHESES 0 TERM_CONSTRAINTS 0"]) registered_roots @
       ["TRANSITIVE_ORACLES 0", "SKIP_PROOF false", summary, ""]);
    (* Export only after every guard succeeds. Path.binding0 is required by
       this pinned Export.export API; the payload is one literal text node. *)
    val _ = Export.export thy (Path.binding0 (Path.basic "endpoint-audit.txt"))
      [XML.Text report];
    val _ = writeln summary;
  in () end;

end;
