package MT::Plugin::PerformanceProfiler::KYTProfLogger;

use strict;
use warnings;
use utf8;

use IO::File;
use IO::Compress::Gzip;
use JSON;
use Digest::SHA1 qw(sha1_hex);

sub new {
    my $class = shift;
    my ( $file_name, $compress, $encoder, $max_file_size, $exceeded_handler )
        = @{ $_[0] }{qw(file_name compress encoder max_file_size exceeded_file_size_handler)};
    my $io
        = $compress
        ? IO::Compress::Gzip->new( $file_name, '-Level' => $compress )
        : IO::File->new( $file_name, 'w' );
    my $self = {
        io               => $io,
        encoder          => $encoder,
        bytes_available  => $max_file_size || undef,
        exceeded_handler => $exceeded_handler,
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

    my $str = join( "\t", $args{time}, $args{package}, $args{line}, $args{data}{sql} ) . "\n";

    $self->{bytes_available} -= length($str) if defined( $self->{bytes_available} );
    if ( defined( $self->{bytes_available} ) && $self->{bytes_available} < 0 ) {
        $self->{exceeded_handler}->();
        return;
    }

    $self->print($str);
}

sub finish {
    my $self = shift;
    my ($meta) = @_;
    $meta ||= {};

    local $meta->{truncated} = $self->{bytes_available} < 0 ? $JSON::true : $JSON::false;
    $self->print( '# ' . $self->{encoder}->encode($meta) . "\n" );

    $self->{io}->close;
}

1;
