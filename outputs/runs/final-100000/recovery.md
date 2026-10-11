# Official run recovery record

The official run was intentionally interrupted after 9,309 source records had been completed. The saved
checkpoint was retained and the same run directory was resumed with five bounded workers. Previously completed
IDs and valid exact-text cache results were not reclassified.

The main resumed pass reached 93,379 completed reviews. Failed batches were retried with batch size 10 and then
batch size 1. Three persistent edge cases were resolved by enforcing the single-record source ID in code and
bounding evidence quotes to 400 characters in the response schema. The final state is 100,000 completed and
zero quarantined.

`checkpoint_before.json` contains the 9,309 pre-interruption IDs; `checkpoint_after.json` contains all 100,000
completed IDs. `calls.jsonl` preserves the initial and resumed call phases, failures, recoveries, and independent
verification calls.
