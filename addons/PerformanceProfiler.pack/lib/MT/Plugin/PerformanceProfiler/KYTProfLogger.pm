package MT::Plugin::PerformanceProfiler::KYTProfLogger;

use strict;
use warnings;
use utf8;

use Digest::SHA1 qw(sha1_hex);

sub new {
    my $class = shift;
    my ( $file_name, $encoder ) = @_;
    open my $fh, '>', $file_name;
    my $self = { fh => $fh, encoder => $encoder };
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
