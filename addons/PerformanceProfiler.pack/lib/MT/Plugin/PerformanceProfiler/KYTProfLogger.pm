package MT::Plugin::PerformanceProfiler::KYTProfLogger;

use strict;
use warnings;
use utf8;

use IO::File;
use IO::Compress::Gzip;
use Digest::SHA1 qw(sha1_hex);

sub new {
    my $class = shift;
    my ( $file_name, $compress, $encoder ) = @{ $_[0] }{qw(file_name compress encoder)};
    my $io
        = $compress
        ? IO::Compress::Gzip->new( $file_name, '-Level' => $compress )
        : IO::File->new( $file_name, 'w' );
    my $self = { io => $io, encoder => $encoder };
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

    my @binds = map { $_ =~ m{\A(?:[0-9]+|undef)?\z} ? $_ : substr( sha1_hex($_), 0, 8 ); }
        split( /, /, ( $args{data}{sql_binds} =~ m{\A\(bind: (.*)\)\z} )[0] );

    $self->print(
        $self->{encoder}->encode(
            {   runtime          => $args{time},
                operation_class  => $args{module},
                operation_method => $args{method},
                caller_package   => $args{package},
                caller_file_name => $args{file},
                caller_line      => $args{line},
                sql              => $args{data}{sql},
                sql_binds        => \@binds,
            }
            )
            . "\n"
    );
}

1;
