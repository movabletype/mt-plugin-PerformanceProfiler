package MT::Plugin::PerformanceProfiler::KYTProfLogger;

use strict;
use warnings;
use utf8;

sub new {
    my $class = shift;
    my ( $file_name, $max_file_size, $exceeded_handler )
        = @{ $_[0] }{qw(file_name max_file_size exceeded_file_size_handler)};
    open my $fh, '>', $file_name;
    my $self = {
        fh               => $fh,
        bytes_available  => $max_file_size || undef,
        exceeded_handler => $exceeded_handler,
    };
    bless $self, $class;
    $self;
}

sub print {
    my $self = shift;
    my ($msg) = @_;
    print { $self->{fh} } $msg;
}

sub log {
    my $self = shift;
    my %args = @_;

    $args{data}{sql} =~ s{(?:\n|\t)+}{ }g;
    $args{data}{sql} =~ s{\s+$}{};
    my $str = join( "\t", $args{time}, $args{package}, $args{line}, $args{data}{sql} ) . "\n";

    $self->{bytes_available} -= length($str) if defined( $self->{bytes_available} );
    if ( defined( $self->{bytes_available} ) && $self->{bytes_available} < 0 ) {
        $self->{exceeded_handler}->();
        return;
    }

    $self->print($str);
}

sub is_truncated {
    my $self = shift;
    defined( $self->{bytes_available} ) && $self->{bytes_available} < 0;
}

1;
