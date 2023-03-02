# Step 0

NOTE: This step mainly exists for documentation purposes. If you *do* build this
step on your own, make sure to walk through the files where there's a reference
to `kkleine/llvm-pgo-37` and change it to your project. I don't see a need to
consider this part of this excersise.

In this step we're going to create PGO instrumented LLVM packages and host them
for later consumption on a Copr project. 

If you want to build this yourself, you need to have a valid Kerberos ticket. Try running:

```
$ kinit <FAS_USER>@FEDORAPROJECT.ORG
```

But rest assured, you don't need to run this on your own. The
[kkleine/llvm-pgo-37](https://copr.fedorainfracloud.org/coprs/kkleine/llvm-pgo-37/)
project is ready for you to consume in the next steps.