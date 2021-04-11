package MT::Plugin::PerformanceProfiler;

use v5.10;
use strict;
use warnings;
use utf8;

use Digest::SHA1 qw(sha1_hex);
use File::Spec;
use File::Basename qw(basename);
use JSON;
use Time::HiRes qw(gettimeofday tv_interval);
use MT::Plugin::PerformanceProfiler::KYTProfLogger;
use MT::Plugin::PerformanceProfiler::Guard;

use constant FILE_PREFIX => 'b-';

our ( $current_file, $current_metadata, $current_start );
our ( $freq, $counter );
our (%profilers);

our $json_encoder = JSON->new->utf8;

sub path {
    state $path = MT->config->PerformanceProfilerPath;
    return $path;
}

sub enabled {
    return !!path();
}

sub enable_profile {
    my ( $file, $metadata ) = @_;

    $current_file     = $file;
    $current_metadata = $metadata;
    $current_start    = [gettimeofday];

    if ( $profilers{KYTProf} ) {
        state $compress = MT->config->PerformanceProfilerCompress;

        # XXX: force re-initialize $Devel::KYTProf::Profiler::DBI::_TRACER
        Devel::KYTProf::Profiler::DBI->apply;
        Devel::KYTProf->logger(
            MT::Plugin::PerformanceProfiler::KYTProfLogger->new(
                {   file_name => sprintf( $file, 'kyt' ),
                    compress  => $compress,
                    encoder   => $json_encoder,
                }
            )
        );
    }

    if ( $profilers{NYTProf} ) {
        DB::enable_profile( sprintf( $file, 'nyt' ) );
    }
}

sub finish_profile_kytprof {

    # FIXME: We want to release DBIx::Tracer in an implementation-independent way
    return unless $Devel::KYTProf::Profiler::DBI::_TRACER;

    Devel::KYTProf->mute($_) for qw(DBI DBI::st DBI::db);
    undef $Devel::KYTProf::Profiler::DBI::_TRACER;
    Devel::KYTProf->_orig_code( {} );
    Devel::KYTProf->_prof_code( {} );
}

sub finish_profile {
    return unless $current_file;

    $current_metadata->{runtime} = tv_interval($current_start);

    if ( $profilers{NYTProf} ) {
        DB::finish_profile();
        my $file = sprintf( $current_file, 'nyt' );
        open my $fh, '>>', $file;
        print {$fh} '# ' . $json_encoder->encode($current_metadata) . "\n";
    }

    if ( $profilers{KYTProf} ) {
        finish_profile_kytprof();
        Devel::KYTProf->logger->print( $json_encoder->encode($current_metadata) . "\n" );
    }

    undef $current_file;
}

sub cancel_profile {
    my $file = $current_file
        or return;

    finish_profile;

    unlink sprintf( $file, 'nyt' ) if $profilers{NYTProf};
    unlink sprintf( $file, 'kyt' ) if $profilers{KYTProf};
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
        next if scalar( @{ $files{$profiler} } ) <= $max_files;

        my @files = map { $_->[1] }
            sort { $b->[0] <=> $a->[0] }
            map  { [ ( stat($_) )[10] => $_ ] } @{ $files{$profiler} };
        for my $f ( @files[ $max_files - 1 .. $#files ] ) {
            unlink $f;
        }
    }
}

sub init_app {
    my $dir = path()
        or return;

    $freq = MT->config->PerformanceProfilerFrequency
        or return;
    $counter = int( rand($freq) );

    %profilers = map { $_ => 1 }
        split( /\s*,\s*/, MT->config('PerformanceProfilerProfilers') );

    if ( $profilers{KYTProf} ) {
        require Devel::KYTProf;
        Devel::KYTProf->apply_prof('DBI');
        Devel::KYTProf->namespace_regex('MT::Template');
        finish_profile_kytprof;
    }

    if ( $profilers{NYTProf} ) {
        my @opts = qw( sigexit=int savesrc=0 start=no );
        $ENV{"NYTPROF"} = join ":", @opts;
        require Devel::NYTProf;
    }

    mkdir $dir unless -d $dir;

    1;
}

sub _build_file_filter {
    my ( $cb, %param ) = @_;

    my $dir = path()
        or return;

    if ( $freq > 1 ) {
        $counter = ( $counter + 1 ) % $freq;
        return unless $counter == 0;
    }

    return unless -d $dir;

    $param{context}->stash( 'performance_profiler_guard',
        MT::Plugin::PerformanceProfiler::Guard->new( \&cancel_profile ) );

    my $filename = sha1_hex( $param{File} );

    remove_old_files();
    enable_profile(
        File::Spec->catfile( $dir, FILE_PREFIX . '%s-' . $filename ),
        {   version         => $MT::VERSION,
            product_version => $MT::PRODUCT_VERSION,
            file            => $param{File},
            archive_type    => $param{ArchiveType},
        },
    );
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

1;
