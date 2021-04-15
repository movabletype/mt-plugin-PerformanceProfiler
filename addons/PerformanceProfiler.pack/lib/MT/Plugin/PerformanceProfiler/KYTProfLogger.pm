package MT::Plugin::PerformanceProfiler::KYTProfLogger;

use strict;
use warnings;
use utf8;

sub new {
    my $class = shift;
    my ( $file_name, $encoder ) = @_;
    open my $fh, '>', $file_name;
    my $self = { fh => $fh, encoder => $encoder, package_map => +{} };
    bless $self, $class;
    $self->print( pack( 'C', 1 ) );    # version 1
    $self;
}

sub print {
    my $self = shift;
    my ($msg) = @_;
    print { $self->{fh} } $msg;
}

sub _package_id {
    my $self = shift;
    my ($package) = @_;
    $self->{package_map}{$package} or do {
        my $next_id = keys( %{ $self->{package_map} } );
        $self->{package_map}{$package} = $next_id;
    };
}

sub log {
    my $self = shift;
    my %args = @_;

    my $time = int( $args{time} * 1000 );    # milliseconds
    if ( $time > 65535 ) {

        # I thing that a single inquiry does not take more than a minute.
        $time = 65535;
    }
    my $package_id = $self->_package_id( $args{package} );

    $self->print( pack( 'nnn', $time, $package_id, $args{line}, ) );
}

sub finish {
    my $self = shift;
    my ($metadata) = @_;

    $metadata->{packages} = [
        map      { $_->[1] }
            sort { $a->[0] <=> $b->[0] }
            map  { [ $self->{package_map}{$_} => $_ ] }
            keys %{ $self->{package_map} }
    ];

    $self->print( "\n" . $self->{encoder}->encode($metadata) . "\n" );

    close $self->{fh};
}

1;
