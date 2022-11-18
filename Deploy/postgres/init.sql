create table test
(
    t_id          bigint                not null
        constraint test_pk
            primary key,
    username      varchar
);

alter table test
    owner to postgres;
