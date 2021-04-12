package MT::Plugin::PerformanceProfiler::KYTProfLogger;

use strict;
use warnings;
use utf8;

use Digest::SHA1 qw(sha1_hex);

sub new {
    my $class = shift;
    my ( $file_name, $encoder, $max_file_size, $exceeded_handler )
        = @{ $_[0] }{qw(file_name encoder max_file_size exceeded_file_size_handler)};
    open my $fh, '>', $file_name;
    my $self = {
        fh               => $fh,
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
    print { $self->{fh} } $msg;
}

sub log {
    my $self = shift;
    my %args = @_;

    my @binds = map { $_ =~ m{\A(?:[0-9]+|undef)?\z} ? $_ : substr( sha1_hex($_), 0, 8 ); }
        split( /, /, ( $args{data}{sql_binds} =~ m{\A\(bind: (.*)\)\z} )[0] );

    my $str = $self->{encoder}->encode(
        {   runtime   => $args{time},
            class     => $args{module},
            method    => $args{method},
            package   => $args{package},
            file_name => $args{file},
            line      => $args{line},
            sql       => $args{data}{sql},
            binds     => \@binds,
        }
    ) . "\n";

    $self->{bytes_available} -= length($str) if defined( $self->{bytes_available} );
    if ( defined( $self->{bytes_available} ) && $self->{bytes_available} < 0 ) {
        $self->{exceeded_handler}->();
        return;
    }

    $self->print($str);
}

1;
