# PerformanceProfiler

This is a plugin for the Movable Type.
This plugin enables you to recored performace profile.


## Installation

1. Download an archive file from [releases](https://github.com/movabletype/mt-plugin-PerformanceProfiler/releases).
1. Unpack an archive file.
1. Upload unpacked files to your MT directory.

Should look like this when installed:

    $MT_HOME/
        addons/
            PerformanceProfiler.pack/

## Environment variable

### PerformanceProfilerProfilers

Comma-separated list of profilers.
Accepts the following values.

* KYTProf
* NYTProf

The default value is "KYTProf".

### PerformanceProfilerPath

The path to output the profile data.
If not specified, it will not be output.

The default value is blank.

### PerformanceProfilerFrequency

The frequency of profiling.

* 0 : Disabled
* 1 : Always recored profile
* 10 : Record profile once in ten times

The default value is "10".

### PerformanceProfilerMaxFiles:

The number of files to save.
If the number of saved files exceeds this number, the oldest one will be deleted.

The default value is "1000".

### PerformanceProfilerMaxFileSize:

Maximum file size to save.
Note: This limitation only works for KYTProf.

The default value is "20971520" (20MB).

## Requirements

* Movable Type 7

## LICENSE

MIT License

Copyright (c) 2021 Six Apart Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
