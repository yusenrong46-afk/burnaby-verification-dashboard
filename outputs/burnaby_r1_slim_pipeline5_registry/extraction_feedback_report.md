# Extraction Feedback

This report translates verifier outcomes into upstream extraction/evidence-span fixes.

- Rows: 104
- Review feedback rows: 81
- Not-used feedback rows: 23

## Category Counts

- `attach_complete_text_span`: 41
- `preserve_table_context`: 33
- `classify_not_used_artifact`: 10
- `cross_reference_or_traceability`: 9
- `administrative_or_discretionary_language`: 4
- `candidate_likely_correct_after_rerun`: 3
- `model_exception_or_legal_condition`: 3
- `better_evidence_available`: 1

## Top 30

- `burnaby_r1_004` `preserve_table_context` -> emit_table_title_row_column_cell: Preserve table title, row header, column header, and cell value together.
- `burnaby_r1_011` `model_exception_or_legal_condition` -> extract_condition_and_exception_fields: Preserve exception/subject-to/covenant wording as structured condition or exception fields before verification.
- `burnaby_r1_012` `preserve_table_context` -> emit_table_title_row_column_cell: Preserve table title, row header, column header, and cell value together.
- `burnaby_r1_013` `preserve_table_context` -> emit_table_title_row_column_cell: Preserve table title, row header, column header, and cell value together.
- `burnaby_r1_014` `preserve_table_context` -> emit_table_title_row_column_cell: Preserve table title, row header, column header, and cell value together.
- `burnaby_r1_015` `preserve_table_context` -> emit_table_title_row_column_cell: Preserve table title, row header, column header, and cell value together.
- `burnaby_r1_016` `preserve_table_context` -> emit_table_title_row_column_cell: Preserve table title, row header, column header, and cell value together.
- `burnaby_r1_017` `preserve_table_context` -> emit_table_title_row_column_cell: Preserve table title, row header, column header, and cell value together.
- `burnaby_r1_018` `preserve_table_context` -> emit_table_title_row_column_cell: Preserve table title, row header, column header, and cell value together.
- `burnaby_r1_019` `preserve_table_context` -> emit_table_title_row_column_cell: Preserve table title, row header, column header, and cell value together.
- `burnaby_r1_020` `preserve_table_context` -> emit_table_title_row_column_cell: Preserve table title, row header, column header, and cell value together.
- `burnaby_r1_021` `preserve_table_context` -> emit_table_title_row_column_cell: Preserve table title, row header, column header, and cell value together.
- `burnaby_r1_022` `preserve_table_context` -> emit_table_title_row_column_cell: Preserve table title, row header, column header, and cell value together.
- `burnaby_r1_023` `preserve_table_context` -> emit_table_title_row_column_cell: Preserve table title, row header, column header, and cell value together.
- `burnaby_r1_024` `preserve_table_context` -> emit_table_title_row_column_cell: Preserve table title, row header, column header, and cell value together.
- `burnaby_r1_025` `preserve_table_context` -> emit_table_title_row_column_cell: Preserve table title, row header, column header, and cell value together.
- `burnaby_r1_026` `better_evidence_available` -> replace_weak_evidence_with_suggested_span: Use the Evidence Intelligence lead as the candidate's cited evidence and rerun verification.
- `burnaby_r1_027` `preserve_table_context` -> emit_table_title_row_column_cell: Preserve table title, row header, column header, and cell value together.
- `burnaby_r1_028` `candidate_likely_correct_after_rerun` -> use_rerun_evidence_in_next_registry: The suggested evidence passed deterministic rerun and is ready for manual promotion review.
- `burnaby_r1_029` `preserve_table_context` -> emit_table_title_row_column_cell: Preserve table title, row header, column header, and cell value together.
- `burnaby_r1_030` `preserve_table_context` -> emit_table_title_row_column_cell: Preserve table title, row header, column header, and cell value together.
- `burnaby_r1_031` `preserve_table_context` -> emit_table_title_row_column_cell: Preserve table title, row header, column header, and cell value together.
- `burnaby_r1_032` `preserve_table_context` -> emit_table_title_row_column_cell: Preserve table title, row header, column header, and cell value together.
- `burnaby_r1_033` `preserve_table_context` -> emit_table_title_row_column_cell: Preserve table title, row header, column header, and cell value together.
- `burnaby_r1_034` `preserve_table_context` -> emit_table_title_row_column_cell: Preserve table title, row header, column header, and cell value together.
- `burnaby_r1_035` `preserve_table_context` -> emit_table_title_row_column_cell: Preserve table title, row header, column header, and cell value together.
- `burnaby_r1_036` `preserve_table_context` -> emit_table_title_row_column_cell: Preserve table title, row header, column header, and cell value together.
- `burnaby_r1_037` `preserve_table_context` -> emit_table_title_row_column_cell: Preserve table title, row header, column header, and cell value together.
- `burnaby_r1_038` `preserve_table_context` -> emit_table_title_row_column_cell: Preserve table title, row header, column header, and cell value together.
- `burnaby_r1_039` `preserve_table_context` -> emit_table_title_row_column_cell: Preserve table title, row header, column header, and cell value together.
