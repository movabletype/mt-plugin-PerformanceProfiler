requires perl => '5.010';

feature 'extlib', 'extlib' => sub {
    requires 'Devel::KYTProf', 0.9994;
    requires 'Class::Data::Lite', 0.0010;
    requires 'DBIx::Tracer', 0.03;
    requires 'Regexp::Trie', 0.02;
}
