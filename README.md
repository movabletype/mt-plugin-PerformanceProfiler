# PerformanceProfiler

This is a plugin for the Movable Type.
This plugin enables you to recored performace profile via Devel::NYTProf.

## Screenshot

![Screenshot](https://raw.githubusercontent.com/usualoma/mt-plugin-PerformanceProfiler/main/artwork/screenshot.png)

## Installation

1. Download an archive file from [releases](https://github.com/usualoma/mt-plugin-PerformanceProfiler/releases).
1. Unpack an archive file.
1. Upload unpacked files to your MT directory.

Should look like this when installed:

    $MT_HOME/
        plugins/
            PerformanceProfiler/

## Environment variable

### PerformanceProfilerPath

The path to output the profile data.
If not specified, it will not be output.

### PerformanceProfilerFrequency

The frequency of profiling.

* 0 : Disabled
* 1 : Always recored profile
* 10 : Record profile once in ten times

### PerformanceProfilerMaxFiles:

The number of files to save.
If the number of saved files exceeds this number, the oldest one will be deleted.

## Required perl modules

* Devel::NYTProf

## Requirements

* Movable Type 7
