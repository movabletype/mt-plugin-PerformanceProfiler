use strict;
use warnings;
use FindBin;
use Cwd;

use lib Cwd::realpath("./t/lib"), "$FindBin::Bin/lib";
use IO::Uncompress::Gunzip;
use JSON;
use Test::More;
use Test::Deep;
use File::Spec;
use File::Temp qw( tempdir );
use MT::Test::Env;

our $test_env;
our $profiler_path;

BEGIN {
    $profiler_path = tempdir( CLEANUP => 1 );
    $test_env      = MT::Test::Env->new(
        PerformanceProfilerPath      => $profiler_path,
        PerformanceProfilerFrequency => 1,
        PerformanceProfilerMaxFiles  => 10,
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

MT->instance->rebuild_indexes( Blog => $blog1 );
my @profiles_for_index        = glob( File::Spec->catfile( $profiler_path, '*' ) );
my @profiles_for_index_ctimes = map { ( stat($_) )[10] } @profiles_for_index;
is scalar(@profiles_for_index), 6;

MT->instance->rebuild( Blog => $blog1 );
my @profiles_for_all = glob( File::Spec->catfile( $profiler_path, '*' ) );
is scalar(@profiles_for_all), 10;
cmp_deeply( [ map { ( stat($_) )[10] } @profiles_for_all ],
    noneof(@profiles_for_index_ctimes), 'removed' );

my $footer = MT::Util::from_json(
    do {
        my $fh = IO::Uncompress::Gunzip->new($profiles_for_all[0]);
        my @lines = <$fh>;
        $lines[-1];
    }
);
ok $footer->{archive_type};
ok $footer->{runtime};
is $footer->{product_version}, $MT::PRODUCT_VERSION;
is $footer->{version},         $MT::VERSION;
is $footer->{truncated},       $JSON::false;

done_testing;
