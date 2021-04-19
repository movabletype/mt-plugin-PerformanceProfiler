use strict;
use warnings;

use Test::More;

use lib qw( lib extlib addons/PerformanceProfiler.pack/lib addons/PerformanceProfiler.pack/extlib );

use_ok 'MT::Plugin::PerformanceProfiler';
use_ok 'MT::Plugin::PerformanceProfiler::Guard';
use_ok 'MT::Plugin::PerformanceProfiler::KYTProfLoggerFactory';
use_ok 'MT::Plugin::PerformanceProfiler::KYTProfLogger::v1';

done_testing;
