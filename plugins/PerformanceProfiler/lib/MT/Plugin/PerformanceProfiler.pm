package MT::Plugin::PerformanceProfiler;

use strict;
use warnings;
use utf8;

use Devel::KYTProf ();

sub component {
    __PACKAGE__ =~ m/::([^:]+)\z/;
}

sub plugin {
    MT->component( component() );
}

sub dir {
    MT->config->PerformanceProfilerPath;
}

sub enabled {
    !!dir();
}

sub enable_profile {
    my ($file) = @_;

    # DB::enable_profile( sprintf( "%s/bf-%s", $dir, $path ) ); # NYTProf

    # XXX: force re-initialize $Devel::KYTProf::Profiler::DBI::_TRACER
    Devel::KYTProf::Profiler::DBI->apply;
    Devel::KYTProf->logger( MT::Plugin::PerformanceProfilerLogger->new( sprintf( $file, 'kyt' ) ) );

}

sub finish_profile {

    # DB::finish_profile(); # NYTProf

    # FIXME: We want to release DBIx::Tracer in an implementation-independent way
    if ($Devel::KYTProf::Profiler::DBI::_TRACER) {
        Devel::KYTProf->mute($_) for qw(DBI DBI::st DBI::db);
        undef $Devel::KYTProf::Profiler::DBI::_TRACER;
        Devel::KYTProf->_orig_code( {} );
        Devel::KYTProf->_prof_code( {} );
    }
}

sub cleanup {
    my $max_files = MT->config->PerformanceProfilerMaxFiles
        or return;    # unlimited
    my @files = map { $_->[1] }
        sort { $b->[0] <=> $a->[0] }
        map  { [ ( stat($_) )[10] => $_ ] }
        grep { -f $_ } glob( dir() . '/b-*' );
    for my $f ( @files[ $max_files - 1 .. $#files ] ) {
        unlink $f;
    }
}

sub init_app {
    my $dir = dir()
        or return;

    Devel::KYTProf->apply_prof('DBI');
    Devel::KYTProf->namespace_regex('MT::Template');

    # NYTProf
    # my @opts = qw( sigexit=int savesrc=0 start=no );
    # $ENV{"NYTPROF"} = join ":", @opts;
    # require Devel::NYTProf;

    mkdir $dir unless -d $dir;

    finish_profile();

    1;
}

sub build_file_filter {
    my ( $cb, %param ) = @_;

    my $dir = dir()
        or return;

    finish_profile();

    my $freq = MT->config->PerformanceProfilerFrequency
        or return;    # disabled
    return unless int( rand($freq) ) == 0;

    return unless -d $dir;

    my $path = $param{File};
    $path =~ s{^/|/$}{}g;
    $path =~ s{[^0-9a-zA-Z_-]}{_}g;

    cleanup();
    enable_profile( sprintf( "%s/b-%%s-%s", $dir, $path ) );

    1;
}

sub build_page {
    my ($cb) = @_;

    enabled() or return;
    finish_profile();

    1;
}

sub take_down {
    my ($cb) = @_;

    enabled() or return;
    finish_profile();

    1;
}

package MT::Plugin::PerformanceProfilerLogger {
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

    sub log {
        my $self = shift;
        my %args = @_;

        my @binds = map {
            $_ =~ m{\A(?:[0-9]+|undef)?\z}
                ? $_
                : substr(MT::Util::Digest::SHA::sha1_hex($_), 0, 8);
        } split( /, /, ( $args{data}{sql_binds} =~ m{\A\(bind: (.*)\)\z} )[0] );

        print { $self->{fh} } MT::Util::to_json(
            {   runtime          => $args{time},
                operation_class  => $args{module},
                operation_method => $args{method},
                caller_package   => $args{package},
                caller_file_name => $args{file},
                caller_line      => $args{line},
                sql              => $args{data}{sql},
                sql_binds        => \@binds,
            }
        ) . "\n";
    }
}

1;
