package MT::Plugin::PerformanceProfiler::KYTProfLoggerFactory;

use strict;
use warnings;
use utf8;

use MT::Plugin::PerformanceProfiler::KYTProfLogger::v1;

sub new_logger {
    my $class = shift;
    MT::Plugin::PerformanceProfiler::KYTProfLogger::v1->new(@_);
}

1;
