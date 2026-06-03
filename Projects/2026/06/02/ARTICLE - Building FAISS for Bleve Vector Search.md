---
title: "Building FAISS for Bleve Vector Search"
aliases:
  - FAISS for Bleve Vector Search
  - Bleve Vectors with FAISS
  - RAG Eval Bleve KNN Experiment
tags:
  - article
  - go
  - bleve
  - faiss
  - vector-search
  - rag
  - cgo
status: active
type: article
created: 2026-06-02
repo: /home/manuel/workspaces/2026-05-27/rag-evaluation-system
---

# Building FAISS for Bleve Vector Search

This report explains how we built the Bleve-maintained FAISS fork, installed the C and C++ shared libraries required by `go-faiss`, and validated Bleve vector search with a small Go experiment. The purpose is not only to preserve the commands. The purpose is to explain why each part of the build matters, how the linker and header problems arise, and what a future developer should check when Bleve vector support fails to compile.

> [!summary]
> - Bleve vector search is enabled by the Go build tag `-tags=vectors`; with that tag, Bleve depends on `github.com/blevesearch/go-faiss`, which uses CGO to call FAISS.
> - The compatible FAISS source for this run was `blevesearch/faiss@fff814d`, built with GPU disabled, C API enabled, shared libraries enabled, and an extra source include path.
> - The final working Go command required explicit `CGO_LDFLAGS="-L/usr/local/lib -lfaiss_c -lfaiss -lstdc++ -lm"` because linking only `-lfaiss_c` left unresolved C++ FAISS symbols.
> - The Bleve KNN experiment indexed 100 documents with vector fields, searched with `SearchRequest.AddKNN`, and verified that the original query document returned as the top hit with score `1.0`.

## Why this work was necessary

The RAG evaluation system already had vector search, but its vector path was not an indexed approximate-nearest-neighbor search. The existing vector search embedded a query, loaded stored embeddings from SQLite, decoded each embedding into `[]float32`, computed cosine similarity in Go, sorted the candidates, and truncated the results. That is a direct brute-force search over a candidate set. It is simple and correct for small sets, but it does not exercise Bleve's vector indexing features and does not validate the stack needed for scalable vector search inside Bleve.

Bleve has a separate vector-search path. When compiled with the `vectors` build tag, it exposes vector field mappings, KNN search requests, and hybrid search paths that can combine text search and vector search. The FAISS dependency is outside the normal pure-Go Bleve build. It is a native C++ library with a C API wrapper, and `go-faiss` reaches it through CGO. This creates three categories of requirements:

1. The correct FAISS headers must be installed in the include layout expected by `go-faiss`.
2. The C API shared library `libfaiss_c.so` and the C++ shared library `libfaiss.so` must both be available.
3. The Go linker must receive enough flags to link the C API library, the C++ FAISS library, and the C++ runtime.

A failure in any one of these areas presents as a different error. Missing headers stop compilation. A missing or mismatched `libfaiss.so` stops linking. An incomplete `CGO_LDFLAGS` value produces a long list of unresolved `faiss::...` symbols. The build work was mostly about making each of these failure modes explicit and then reducing them to a repeatable command sequence.

## The relevant architecture

The vector-search stack has four layers. Each layer has a different responsibility, and the build crosses language boundaries between the second and third layers.

```mermaid
flowchart TD
    A[Go experiment command] --> B[Bleve v2]
    B --> C[go-faiss CGO bindings]
    C --> D[FAISS C API: libfaiss_c.so]
    D --> E[FAISS C++ library: libfaiss.so]

    A --> A1[cmd/experiments/bleve-knn/main.go]
    B --> B1[Vector field mapping and SearchRequest.AddKNN]
    C --> C1[Headers under /usr/local/include/faiss]
    D --> D1[/usr/local/lib/libfaiss_c.so]
    E --> E1[/usr/local/lib/libfaiss.so]
```

The experiment command is ordinary Go code. It creates a Bleve index, defines a vector field, indexes documents, and runs KNN and hybrid queries. Bleve is the search abstraction that the application uses. `go-faiss` is not directly imported by the experiment; it is pulled in by Bleve when the `vectors` tag is enabled. FAISS itself is native code. The Go toolchain delegates native compilation and linking to CGO and the platform linker.

This separation explains why the build can fail after normal Go code is correct. A Go compile error in the experiment is a source-level issue. A missing `IndexBinary_c_ex.h` error means the C header installation is wrong. An unresolved `faiss::IndexFlat::search(...)` symbol means the final link command did not include the C++ FAISS library.

## The source version that worked

The working source was the Bleve-maintained FAISS fork at commit `fff814d`:

```bash
cd /home/manuel/workspaces/2026-05-27/rag-evaluation-system
git clone https://github.com/blevesearch/faiss.git faiss
cd faiss
git checkout fff814d
```

Using the Bleve fork matters. The Go module `github.com/blevesearch/go-faiss` expects headers that are present in this fork and layout. One important header was:

```text
/usr/local/include/faiss/c_api/IndexBinary_c_ex.h
```

An older system FAISS installation had `libfaiss_c.so` in `/usr/local/lib`, but did not have this header installed. That old installation was not sufficient for Bleve v2.6.0 vector builds.

## Configuring FAISS

The CMake configuration that worked was:

```bash
cd /home/manuel/workspaces/2026-05-27/rag-evaluation-system/faiss

rm -rf build
mkdir -p build

cmake -B build \
  -DFAISS_ENABLE_GPU=OFF \
  -DFAISS_ENABLE_C_API=ON \
  -DBUILD_SHARED_LIBS=ON \
  -DFAISS_ENABLE_PYTHON=OFF \
  -DCMAKE_INSTALL_PREFIX=/usr/local \
  -DCMAKE_CXX_FLAGS="-I$PWD" \
  .
```

Each flag has a specific purpose.

| Flag | Reason |
|---|---|
| `-DFAISS_ENABLE_GPU=OFF` | The target was CPU vector search. GPU support adds CUDA requirements that were not needed for this validation. |
| `-DFAISS_ENABLE_C_API=ON` | `go-faiss` calls the C API, so `libfaiss_c.so` must be built. |
| `-DBUILD_SHARED_LIBS=ON` | The Go program links shared libraries through CGO. |
| `-DFAISS_ENABLE_PYTHON=OFF` | Python bindings are unrelated to Bleve vector search and add unnecessary build surface. |
| `-DCMAKE_INSTALL_PREFIX=/usr/local` | Installs headers and libraries where the system linker and default include paths can find them. |
| `-DCMAKE_CXX_FLAGS="-I$PWD"` | Lets the C API build find headers from the source-tree layout, including fork-specific FAISS headers. |

The extra `-I$PWD` flag was not cosmetic. Without it, the C API build failed while looking for FAISS headers from the repository root. The source tree and installed header tree are not the same environment. During the build, the compiler must be able to resolve includes from the checked-out source layout.

## Building the required targets

For Bleve vector support, only two FAISS build targets were required:

```bash
make -C build -j$(nproc) faiss faiss_c
```

Those targets produced:

```text
build/faiss/libfaiss.so
build/c_api/libfaiss_c.so
```

This is enough for the Go experiment if the headers are installed and the Go linker receives the right flags. The full FAISS tree includes tests and benchmarks, which are useful for validating the local checkout but are not required for Bleve.

## The full build failure in `test_hamming.cpp`

A full build with:

```bash
make -C build -j$(nproc)
```

initially failed in `tests/test_hamming.cpp` with a type mismatch like:

```text
invalid conversion from ‘long long int*’ to ‘faiss::HeapArray<faiss::CMax<int, long int> >::TI*’ {aka ‘long int*’}
```

The failure was in test code, not the FAISS libraries used by Bleve. The important point is the C++ type distinction. On this platform, `faiss::int_maxheap_array_t` expected an `ids` buffer whose pointer type was `long int*`. The test used `std::vector<long long>`, so `ids_gen.data()` returned `long long int*`. Both types may be 64-bit on the same machine, but they are not the same C++ type, and the heap result struct requires exact pointer compatibility.

The correct fix was to derive the test vector type from FAISS itself:

```cpp
using HammingHeap = faiss::int_maxheap_array_t;
using HammingHeapId = HammingHeap::TI;
```

Then the hamming test's id containers were changed from hard-coded integer types to `HammingHeapId`:

```cpp
std::shared_ptr<std::vector<HammingHeapId>> true_ids;
std::set<HammingHeapId> correct_ids;
std::vector<HammingHeapId> ids_gen(na * k);
std::vector<HammingHeapId> ids_ham_knn(na * k, 0);
HammingHeap res = {na, k, ids_gen.data(), dist_gen.data()};
```

This fix is better than a cast. A cast would suppress the compiler error while leaving the container element type different from the heap's declared pointer type. Using `HammingHeap::TI` makes the test follow FAISS's own type definition on any platform where `int64_t` aliases to `long` or `long long`.

After the source patch, one more failure appeared:

```text
fatal error: opening dependency file CMakeFiles/faiss_test.dir/test_hamming.cpp.o.d: Permission denied
```

That error was caused by a root-owned generated dependency file in the build tree. Removing the file allowed the user-owned build to proceed:

```bash
rm -f build/tests/CMakeFiles/faiss_test.dir/test_hamming.cpp.o.d
make -C build -j$(nproc)
```

The full FAISS build then completed successfully, including `faiss_test`.

## Installing headers and libraries

The normal install step was:

```bash
cd /home/manuel/workspaces/2026-05-27/rag-evaluation-system/faiss
sudo make -C build install
sudo ldconfig
```

The install had to be verified rather than assumed. The important checks were:

```bash
ls -lh \
  /usr/local/include/faiss/c_api/IndexBinary_c_ex.h \
  /usr/local/lib/libfaiss.so \
  /usr/local/lib/libfaiss_c.so

ldconfig -p | grep -E 'libfaiss(_c)?\.so'
```

The first install attempt updated the C API library and headers, but did not leave a fresh `libfaiss.so` in `/usr/local/lib`. The visible symptom was that `/usr/local/lib/libfaiss_c.so` had the new timestamp and size, while `/usr/local/lib/libfaiss.so` still looked like an older 2025 build. The vector experiment could still run against the local build directories, but system-only linking failed until the fresh `libfaiss.so` was installed as well.

The final installed state had:

```text
/usr/local/include/faiss/c_api/IndexBinary_c_ex.h
/usr/local/lib/libfaiss_c.so
/usr/local/lib/libfaiss.so
```

and `ldconfig` listed both shared libraries.

## The Go linker problem

After the fresh system install was in place, this command still failed:

```bash
GOWORK=off go run -tags=vectors -ldflags "-r /usr/local/lib" ./cmd/experiments/bleve-knn/
```

The linker error contained many unresolved C++ FAISS symbols from `/usr/local/lib/libfaiss_c.so`, such as constructors, virtual tables, typeinfo entries, and search methods under the `faiss::` namespace. The final Go link command included `-lfaiss_c`, but did not include `-lfaiss`.

This is the core linker rule for this setup: the final Go link must include both the C API library and the C++ FAISS library.

The working command was:

```bash
cd /home/manuel/workspaces/2026-05-27/rag-evaluation-system/2026-05-27--rag-evaluation-system

GOWORK=off \
CGO_LDFLAGS="-L/usr/local/lib -lfaiss_c -lfaiss -lstdc++ -lm" \
go run -tags=vectors -ldflags "-r /usr/local/lib" ./cmd/experiments/bleve-knn/
```

The `-r /usr/local/lib` linker flag embeds a runtime search path so the executable can find the shared libraries. The `CGO_LDFLAGS` value supplies the libraries needed for the native link step.

## The Bleve experiment

The experiment lives at:

```text
/home/manuel/workspaces/2026-05-27/rag-evaluation-system/2026-05-27--rag-evaluation-system/cmd/experiments/bleve-knn/main.go
```

The file starts with a build constraint:

```go
//go:build vectors
```

That is intentional. The experiment should not build in an environment where Bleve vector support is disabled. The build tag makes the dependency explicit.

The experiment performs five steps:

1. Create a Bleve index with a vector field.
2. Index 100 synthetic chunk documents with random unit vectors.
3. Run pure KNN search using the vector from `chunk-042` as the query vector.
4. Run hybrid BM25 plus KNN search with RRF scoring.
5. Run BM25-only search for comparison.

The mapping defines a vector field named `embedding`:

```go
embeddingFieldMapping := bleve.NewVectorFieldMapping()
embeddingFieldMapping.Dims = dims
embeddingFieldMapping.Similarity = index.CosineSimilarity
embeddingFieldMapping.VectorIndexOptimizedFor = index.IndexOptimizedForRecall
```

The document type is small:

```go
type indexedChunk struct {
    ChunkID    string    `json:"chunk_id"`
    DocumentID string    `json:"document_id"`
    Text       string    `json:"text"`
    Embedding  []float32 `json:"embedding"`
}
```

The KNN search request is built by adding a KNN clause to a normal Bleve search request:

```go
searchRequest := bleve.NewSearchRequest(bleve.NewMatchNoneQuery())
searchRequest.AddKNN("embedding", queryVector, int64(k), 1.0)
searchRequest.Fields = []string{"chunk_id", "document_id", "text"}
```

The hybrid request combines a text query and a KNN request, then selects reciprocal-rank-fusion scoring:

```go
searchRequest2 := bleve.NewSearchRequest(bleve.NewMatchQuery(textQuery))
searchRequest2.AddKNN("embedding", queryVector, int64(k*2), 1.0)
searchRequest2.Score = "rrf"
searchRequest2.Fields = []string{"chunk_id", "document_id", "text"}
searchRequest2.Size = k
```

The experiment keeps the generated vectors in memory so it can query with the original vector for `chunk-042`. This was a deliberate correction. Bleve's `index.Document` API exposes fields through visitors, not through a direct `Fields` slice, and the indexed vector should not be treated as application storage. Keeping the generated vector in the experiment's own data structure makes the query path explicit.

## Successful output

The system-installed FAISS run succeeded with the explicit `CGO_LDFLAGS` value. The KNN section showed the expected self-match:

```text
=== Step 3: Pure KNN search (no text query) ===
Using embedding from chunk-042 as query vector
KNN search returned 5 hits (total=5, maxScore=1.0000, took=587.151µs)
  1. id=chunk-042 score=1.000000 chunk_id=chunk-042 text="This is chunk number 42 about topic 2."
```

This output validates the important part of the stack. The vector field was indexed. The query vector reached the FAISS-backed KNN path. Bleve returned the document whose vector exactly matched the query vector as the top hit with score `1.0`.

The hybrid section also returned results, with `chunk-042` ranked first in the observed run:

```text
=== Step 4: Hybrid search (BM25 + KNN with RRF fusion) ===
Text query: "topic 2"
Hybrid search returned 5 hits (total=5, maxScore=0.0318, took=504.546µs)
  1. id=chunk-042 score=0.031778 chunk_id=chunk-042 text="This is chunk number 42 about topic 2."
```

The BM25-only section returned text-only matches for comparison. That comparison matters because it shows that the KNN and hybrid paths are not merely calling the normal text search code. The KNN search can rank documents by vector similarity even when the text field is not the ranking source.

## What this changes for RAG evaluation

The current RAG evaluation system has a working vector-search path, but it is a brute-force path over stored embeddings. Bleve with FAISS changes the storage and query model. Instead of decoding many embedding blobs and computing cosine similarity in application code, vectors become indexed fields inside Bleve. Query execution can then use Bleve's KNN request path and hybrid scoring machinery.

The important difference is not only performance. It is also integration. Once vectors live in the Bleve index, the application can express text search, vector search, and hybrid search through one search request structure. That creates a cleaner path for a future `goja-bleve` module: JavaScript scripts can build mappings, index chunk records, add KNN clauses, and choose scoring strategies without separately coordinating a SQLite vector scan and a BM25 query.

A future production migration still needs more work:

- The experiment uses synthetic random vectors; production code should index real chunk embeddings.
- The experiment uses a small in-memory-style workflow with a temporary index path; production code needs lifecycle, persistence, and rebuild policy.
- The experiment validates API mechanics, not retrieval quality.
- The final build command still requires explicit native linker flags, so CI and developer setup need documented environment variables or Makefile targets.

The experiment is nevertheless enough to prove the dependency stack. The native FAISS library can be built. Bleve can compile with vector support. A Go program can index vector fields and run KNN and hybrid search.

## Working rules for future builds

The most useful rules from this work are precise and operational:

- Use `blevesearch/faiss@fff814d` for the Bleve v2.6.0 vector stack used in this workspace.
- Configure FAISS with `FAISS_ENABLE_C_API=ON` and `BUILD_SHARED_LIBS=ON`; `libfaiss_c.so` is required by `go-faiss`.
- Keep `-DCMAKE_CXX_FLAGS="-I$PWD"` in the CMake command unless the source layout or fork changes.
- Build `faiss` and `faiss_c` targets first; full test builds are useful but not required for Bleve.
- If `test_hamming.cpp` fails on `long` versus `long long`, use `faiss::int_maxheap_array_t::TI`, not a cast.
- Verify headers and both shared libraries after install; do not assume `make install` updated every artifact.
- For Go vector builds, use `-tags=vectors` and explicit `CGO_LDFLAGS` including both `-lfaiss_c` and `-lfaiss`.
- Keep the runtime library search path explicit with `-ldflags "-r /usr/local/lib"` unless the deployment environment has another reliable loader configuration.

## Final command sequence

The final known-good build and experiment commands were:

```bash
# Build FAISS
cd /home/manuel/workspaces/2026-05-27/rag-evaluation-system/faiss
rm -rf build
cmake -B build \
  -DFAISS_ENABLE_GPU=OFF \
  -DFAISS_ENABLE_C_API=ON \
  -DBUILD_SHARED_LIBS=ON \
  -DFAISS_ENABLE_PYTHON=OFF \
  -DCMAKE_INSTALL_PREFIX=/usr/local \
  -DCMAKE_CXX_FLAGS="-I$PWD" \
  .
make -C build -j$(nproc) faiss faiss_c
sudo make -C build install
sudo ldconfig

# Run Bleve vector experiment
cd /home/manuel/workspaces/2026-05-27/rag-evaluation-system/2026-05-27--rag-evaluation-system
GOWORK=off \
CGO_LDFLAGS="-L/usr/local/lib -lfaiss_c -lfaiss -lstdc++ -lm" \
go run -tags=vectors -ldflags "-r /usr/local/lib" ./cmd/experiments/bleve-knn/
```

## Related source material

The main local files for this work are:

- `/home/manuel/workspaces/2026-05-27/rag-evaluation-system/faiss/tests/test_hamming.cpp` — local patch for full FAISS test build.
- `/home/manuel/workspaces/2026-05-27/rag-evaluation-system/2026-05-27--rag-evaluation-system/cmd/experiments/bleve-knn/main.go` — verified Bleve KNN experiment.
- `/home/manuel/workspaces/2026-05-27/rag-evaluation-system/2026-05-27--rag-evaluation-system/docs/howto-compile-faiss-for-bleve-vectors.md` — operational how-to for rebuilding FAISS.
- `/home/manuel/workspaces/2026-05-27/rag-evaluation-system/goja-bleve/ttmp/2026/06/02/RAGEVAL-GOJA-RAG-STRATEGIES--goja-bleve-bleve-bindings-for-goja-javascript-runtime/reference/01-investigation-diary.md` — detailed investigation diary.

The main result is that Bleve vector search is now validated in this workspace. The next step is to make the native build assumptions easier to reuse: a Makefile target or CI job should encode the final `CGO_LDFLAGS`, `-tags=vectors`, and runtime path flags so the working command does not remain tribal knowledge.
