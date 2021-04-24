package MT::Plugin::PerformanceProfiler::KYTProfLogger::v1;

use strict;
use warnings;
use utf8;

use constant PACK_RECORD => 'nnnn';

our $terminator = pack( PACK_RECORD, (0) x length(PACK_RECORD) );

sub new {
    my $class = shift;
    my ($opts) = @_;
    my ( $file_name, $encoder ) = @$opts{qw(file_name encoder)};
    open my $fh, '>', $file_name;
    my $self = {
        fh            => $fh,
        encoder       => $encoder,
        package_map   => +{},
        package_index => 0,
        sql_map       => +{},
        sql_index     => 0,
    };
    bless $self, $class;
    $self->print( pack( 'C', 1 ) );    # version 1
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

    my $time = int( $args{time} * 1000 + 0.5 );    # milliseconds
    if ( $time > 65535 ) {

        # I thing that a single inquiry does not take more than a minute.
        $time = 65535;
    }
    my $package_index = $self->{package_map}{ $args{package} } ||= $self->{package_index}++;
    my $sql_index     = $self->{sql_map}{ $args{data}{sql} }   ||= $self->{sql_index}++;

    $self->print( pack( PACK_RECORD, $time, $package_index, $args{line}, $sql_index ) );
}

sub finish {
    my $self = shift;
    my ($metadata) = @_;

    # log records are no longer added
    $self->print($terminator);

    $metadata->{packages} = [
        map      { $_->[1] }
            sort { $a->[0] <=> $b->[0] }
            map  { [ $self->{package_map}{$_} => $_ ] }
            keys %{ $self->{package_map} }
    ];
    $self->print( $self->{encoder}->encode($metadata) . "\0" );

    my @sqls = map { $_->[1] }
        sort { $a->[0] <=> $b->[0] }
        map  { [ $self->{sql_map}{$_} => $_ ] }
        keys %{ $self->{sql_map} };
    for my $sql (@sqls) {
        $self->print( $sql . "\0" );
    }

    close $self->{fh};
}

1;
