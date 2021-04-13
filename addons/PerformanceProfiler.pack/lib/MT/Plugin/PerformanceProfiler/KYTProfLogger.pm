package MT::Plugin::PerformanceProfiler::KYTProfLogger;

use strict;
use warnings;
use utf8;

use boolean qw(true false);
use IO::File;
use IO::Compress::Gzip;
use Digest::SHA1 qw(sha1_hex);

sub new {
    my $class = shift;
    my ( $file_name, $compress, $encoder, $max_file_size )
        = @{ $_[0] }{qw(file_name compress encoder max_file_size)};
    my $io
        = $compress
        ? IO::Compress::Gzip->new( $file_name, '-Level' => $compress )
        : IO::File->new( $file_name, 'w' );
    my $self = {
        io              => $io,
        encoder         => $encoder,
        bytes_available => $max_file_size || undef,
    };
    bless $self, $class;
    $self;
}

sub print {
    my $self = shift;
    my ($msg) = @_;
    $self->{io}->print($msg);
}

sub log {
    my $self = shift;
    my %args = @_;

    return if defined( $self->{bytes_available} ) && $self->{bytes_available} < 0;

    my @binds = map { $_ =~ m{\A(?:[0-9]+|undef)?\z} ? $_ : substr( sha1_hex($_), 0, 8 ); }
        split( /, /, ( $args{data}{sql_binds} =~ m{\A\(bind: (.*)\)\z} )[0] );

    my $str = $self->{encoder}->encode(
        {   runtime   => $args{time},
            package   => $args{package},
            line      => $args{line},
            sql       => $args{data}{sql},
            binds     => \@binds,
        }
    ) . "\n";

    $self->{bytes_available} -= length($str) if defined( $self->{bytes_available} );
    $self->print($str);
}

sub finish {
    my $self = shift;
    my ($meta) = @_;
    $meta ||= {};

    local $meta->{truncated} = $self->{bytes_available} < 0 ? true : false;
    $self->print( $self->{encoder}->encode($meta) . "\n" );

    $self->{io}->close;
}

1;
