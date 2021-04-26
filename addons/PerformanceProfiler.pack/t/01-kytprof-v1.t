use strict;
use warnings;
use FindBin;
use Cwd;

use lib Cwd::realpath("./t/lib"), "$FindBin::Bin/lib";
use Time::Piece;
use Test::More;
use Test::Deep;
use File::Spec;
use File::Temp qw( tempdir );
use MT::Test::Env;

use_ok 'MT::Plugin::PerformanceProfiler::KYTProfLogger::v1';

our $test_env;
our $profiler_path;

BEGIN {
    $profiler_path = tempdir( CLEANUP => 1 );
    $test_env      = MT::Test::Env->new(
        PerformanceProfilerPath      => $profiler_path,
        PerformanceProfilerFrequency => 1,
        PluginPath                   => [ Cwd::realpath("$FindBin::Bin/../../../addons") ],
    );

    $ENV{MT_APP}    = 'MT::App::CMS';
    $ENV{MT_CONFIG} = $test_env->config_file;
}

use MT;
use MT::Test;
use MT::Test::Fixture;
use MT::Test::Permission;
use MT::Association;

MT::Test->init_app;

$test_env->prepare_fixture('db');

my $blog1_name = 'PerformanceProfiler-' . time();
my $super      = 'super';

my $objs = MT::Test::Fixture->prepare(
    {   author  => [ { 'name' => $super }, ],
        website => [
            {   name     => $blog1_name,
                site_url => 'http://example.com/blog/',
            },
        ],
        entry => [
            map {
                my $name = 'PerformanceProfilerEntry-' . $_ . time();
                +{  basename    => $name,
                    title       => $name,
                    author      => $super,
                    status      => 'publish',
                    authored_on => '20190703121110',
                    },
            } ( 1 .. 10 )
        ],
    }
);

my $blog1 = MT->model('website')->load( { name => $blog1_name } ) or die;
my $time_start = gmtime();

MT->instance->rebuild_indexes( Blog => $blog1 );
my @profiles_for_index        = glob( File::Spec->catfile( $profiler_path, '*', '*' ) );
my @profiles_for_index_ctimes = map { ( stat($_) )[10] } @profiles_for_index;
is scalar(@profiles_for_index), 6;

MT->instance->rebuild( Blog => $blog1 );
my @profiles_for_all = glob( File::Spec->catfile( $profiler_path, '*', '*' ) );
is scalar(@profiles_for_all), 23;

my $time_end = gmtime();

subtest 'with parser cli', sub {
    my $cli = "$FindBin::Bin/../../../tools/PerformanceProfiler.pack/main.py";
    `$cli --help 2>&1`;
    if ($?) {
        plan skip_all => 'The runtime environment of cli is not ready';
    }

    my ($file) = @profiles_for_all;
    my $data = MT::Util::from_json(`$cli dump $file`);
    my $time = Time::Piece->strptime($data->{build}{timestamp}, "%Y-%m-%dT%H:%M:%SZ");

    is $data->{version}, 1;
    ok $data->{build}{archive_type};
    ok $time >= $time_start && $time <= $time_end;
    ok $data->{build}{runtime};
    is $data->{build}{product_version}, $MT::PRODUCT_VERSION;
    is $data->{build}{version},         $MT::VERSION;

    my ($log) = @{$data->{logs}};

    ok $log->{runtime};
    like $log->{package}, qr/^MT::/;
    ok $log->{line};
    like $log->{query}, qr/^SELECT/i;
};

done_testing;
