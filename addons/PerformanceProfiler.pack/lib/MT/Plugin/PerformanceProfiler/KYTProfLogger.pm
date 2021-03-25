package MT::Plugin::PerformanceProfiler::KYTProfLogger;

use strict;
use warnings;
use utf8;

use MT::Util ();
use MT::Util::Digest::SHA;

sub new {
    my $class = shift;
    my ($file_name) = @_;
    open my $fh, '>', $file_name;
    my $self = { fh => $fh };
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

    my @binds = map {
              $_ =~ m{\A(?:[0-9]+|undef)?\z}
            ? $_
            : substr( MT::Util::Digest::SHA::sha1_hex($_), 0, 8 );
    } split( /, /, ( $args{data}{sql_binds} =~ m{\A\(bind: (.*)\)\z} )[0] );

    $self->print(
        MT::Util::to_json(
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
