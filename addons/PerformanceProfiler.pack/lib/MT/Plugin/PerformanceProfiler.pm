package MT::Plugin::PerformanceProfiler;

use strict;
use warnings;
use utf8;

use File::Spec;
use File::Basename qw(basename);
use MT::Util ();
use MT::Plugin::PerformanceProfiler::KYTProfLogger;

use constant FILE_PREFIX => 'b-';

our $current_file;

sub path {
    MT->config->PerformanceProfilerPath;
}

sub enabled {
    return !!path();
}

sub profiler_enabled {
    my ($profiler) = @_;
    return grep { $_ eq $profiler }
        split( /\s*,\s*/, MT->config('PerformanceProfilerProfilers') );
}

sub enable_profile {
    my ($file) = @_;

    $current_file = $file;

    if ( profiler_enabled('KYTProf') ) {

        # XXX: force re-initialize $Devel::KYTProf::Profiler::DBI::_TRACER
        Devel::KYTProf::Profiler::DBI->apply;
        Devel::KYTProf->logger(
            MT::Plugin::PerformanceProfiler::KYTProfLogger->new( sprintf( $file, 'kyt' ) ) );
    }

    if ( profiler_enabled('NYTProf') ) {
        DB::enable_profile( sprintf( $file, 'nyt' ) );
    }
}

sub finish_profile {
    return unless $current_file;

    if ( profiler_enabled('NYTProf') ) {
        DB::finish_profile();
        my $file = sprintf( $current_file, 'nyt' );
        open my $fh, '>>', $file;
        print {$fh} '# '
            . MT::Util::to_json(
            {   VERSION         => $MT::VERSION,
                PRODUCT_VERSION => $MT::PRODUCT_VERSION,
            }
            ) . "\n";
    }

    if ( profiler_enabled('KYTProf') ) {

        # FIXME: We want to release DBIx::Tracer in an implementation-independent way
        if ($Devel::KYTProf::Profiler::DBI::_TRACER) {
            Devel::KYTProf->mute($_) for qw(DBI DBI::st DBI::db);
            undef $Devel::KYTProf::Profiler::DBI::_TRACER;
            Devel::KYTProf->_orig_code( {} );
            Devel::KYTProf->_prof_code( {} );
        }
    }

    undef $current_file;
}

sub remove_old_files {
    my $max_files = MT->config->PerformanceProfilerMaxFiles
        or return;    # unlimited

    my %files = ();
    for my $f ( grep { -f $_ } glob( File::Spec->catfile( path(), FILE_PREFIX . '*' ) ) ) {
        my $bn = basename($f);
        my ($profiler) = $bn =~ m/@{[FILE_PREFIX()]}([a-zA-Z]+)/;
        $files{$profiler} ||= [];
        push @{ $files{$profiler} }, $f;
    }

    for my $profiler ( keys %files ) {
        my @files = map { $_->[1] }
            sort { $b->[0] <=> $a->[0] }
            map { [ ( stat($_) )[10] => $_ ] } @{ $files{$profiler} };
        for my $f ( @files[ $max_files - 1 .. $#files ] ) {
            unlink $f;
        }
    }
}

sub init_app {
    my $dir = path()
        or return;

    if ( profiler_enabled('KYTProf') ) {
        require Devel::KYTProf;
        Devel::KYTProf->apply_prof('DBI');
        Devel::KYTProf->namespace_regex('MT::Template');
    }

    if ( profiler_enabled('NYTProf') ) {
        my @opts = qw( sigexit=int savesrc=0 start=no );
        $ENV{"NYTPROF"} = join ":", @opts;
        require Devel::NYTProf;
    }

    mkdir $dir unless -d $dir;

    finish_profile();

    1;
}

sub _build_file_filter {
    my ( $cb, %param ) = @_;

    my $dir = path()
        or return;

    finish_profile();

    my $freq = MT->config->PerformanceProfilerFrequency
        or return;    # disabled
    return unless int( rand($freq) ) == 0;

    return unless -d $dir;

    my $filename = $param{File};
    $filename =~ s{^/|/$}{}g;
    $filename =~ s{[^0-9a-zA-Z_-]}{_}g;

    remove_old_files();
    enable_profile( File::Spec->catfile( $dir, FILE_PREFIX . '%s-' . $filename ) );
}

sub build_file_filter {
    _build_file_filter(@_);
    1;    # always returns true
}

sub build_page {
    my ($cb) = @_;

    return 1 unless enabled();
    finish_profile();

    1;
}

sub take_down {
    my ($cb) = @_;

    return 1 unless enabled();
    finish_profile();

    1;
}

1;
