package MT::Plugin::PerformanceProfiler::Guard;

use strict;
use warnings;
use utf8;

sub new {
    my $class     = shift;
    my ($handler) = @_;
    my $self      = { handler => $handler };
    bless $self, $class;
    $self;
}

sub DESTROY {
    my $self = shift;
    $self->{handler}->();
}

1;
