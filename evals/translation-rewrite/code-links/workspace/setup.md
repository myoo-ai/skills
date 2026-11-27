# Setting up the Lanternfish development environment

## Introduction

This guide walks you through the process of setting up a fully functional development environment for Lanternfish. By following these steps, you will be able to build the project, run the test suite and start contributing in no time. The entire process typically takes less than 15 minutes on a modern machine.

## Prerequisites

Before you begin, it is important to ensure that your system meets the necessary requirements. Lanternfish requires Go 1.27 or later and a working installation of PostgreSQL 17. You can download Go from the [official website](https://go.dev/dl/) and PostgreSQL from the [PostgreSQL downloads page](https://www.postgresql.org/download/).

## Cloning the repository

The first step is to obtain a local copy of the source code. Open a terminal and run the following command:

```sh
git clone https://github.com/lanternfish/lanternfish.git
cd lanternfish
```

## Configuring the database

Lanternfish relies on a dedicated database for its integration tests. Create the database and apply the schema with these commands:

```sh
createdb lanternfish_test
psql lanternfish_test < schema/schema.sql
```

Make sure that the `LANTERNFISH_DB` environment variable points to this database before running any tests.

## Running the tests

Once everything is configured, you can verify your setup by running `make test`. If all tests pass, your environment is ready and you can start working on your first contribution. For further details, please refer to the [contributor guide](https://github.com/lanternfish/lanternfish/blob/main/CONTRIBUTING.md).
