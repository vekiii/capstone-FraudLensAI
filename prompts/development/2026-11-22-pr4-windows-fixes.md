# PR #4 Windows fixes and publication — 2026-11-22

> Океј, ако се слажеш, пушуј ово, па онда настави са тим што си замислио. Или само настави без пушовања, па онда све одједном комитуј и пушуј, како год мислиш да је најбоље. Али ако сам те добро разумео, хоћеш да радиш на овом пул реквесту 4 i na toj grani? Ако је тако, слажем се за комите и пушове за ово што си рекао, слободно можеш да наставиш.

The scope follows the [Windows review findings](../../evidence/tasks/pr4-windows-review-2026-11-22.md).
Fix the publisher and test SQLite lifetimes, add direct synthetic publisher coverage,
require an independent bridge manifest digest in both consumers, and repeat Windows
verification. Publish the verified source and evidence commits on
`integration/model-rag-handoff`, the source branch for PR #4. The merge decision
and any live-provider check remain separate.
