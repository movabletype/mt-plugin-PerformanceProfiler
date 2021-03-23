package MT::Plugin::PerformanceProfiler;

use strict;
use warnings;
use utf8;

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

sub cleanup {
    my $max_files = MT->config->PerformanceProfilerMaxFiles
        or return;    # unlimited
    my @files = map { $_->[1] }
        sort { $b->[0] <=> $a->[0] }
        map  { [ ( stat($_) )[10] => $_ ] }
        grep { -f $_ } glob( dir() . '/bf-*' );
    for my $f ( @files[ $max_files - 1 .. $#files ] ) {
        unlink $f;
    }
}

sub init_app {
    my $dir = dir()
        or return;

    my @opts = qw( sigexit=int savesrc=0 start=no );
    $ENV{"NYTPROF"} = join ":", @opts;
    require Devel::NYTProf;

    mkdir $dir unless -d $dir;

    1;
}

sub build_file_filter {
    my ( $cb, %param ) = @_;

    my $dir = dir()
        or return;

    DB::finish_profile();

    my $freq = MT->config->PerformanceProfilerFrequency
        or return;    # disabled
    return unless int( rand($freq) ) == 0;

    return unless -d $dir;

    my $path = $param{File};
    $path =~ s{^/|/$}{}g;
    $path =~ s{[^0-9a-zA-Z_-]}{_}g;

    cleanup();
    DB::enable_profile( sprintf( "%s/bf-%s", $dir, $path ) );

    1;
}

sub build_page {
    my ($cb) = @_;

    enabled() or return;

    DB::finish_profile();
    1;
}

sub take_down {
    my ($cb) = @_;

    enabled() or return;

    DB::finish_profile();
    1;
}

1;
