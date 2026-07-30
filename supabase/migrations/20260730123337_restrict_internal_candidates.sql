create policy "Internal candidate batches are never publicly readable"
on public.source_candidate_batches
for select
to anon, authenticated
using (false);

create policy "Internal candidates are never publicly readable"
on public.source_candidates
for select
to anon, authenticated
using (false);
