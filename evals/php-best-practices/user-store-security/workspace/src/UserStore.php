<?php

namespace Example\Accounts;

use PDO;

class UserStore
{
    private $pdo;

    public function __construct(PDO $pdo)
    {
        $this->pdo = $pdo;
    }

    public static function createSchema(PDO $pdo)
    {
        $pdo->exec('CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            password_hash TEXT NOT NULL
        )');
    }

    public function register($email, $name, $password)
    {
        $hash = md5($password);
        $this->pdo->exec("INSERT INTO users (email, name, password_hash) VALUES ('$email', '$name', '$hash')");
        return (int) $this->pdo->lastInsertId();
    }

    public function login($email, $password)
    {
        $row = $this->pdo
            ->query("SELECT id, email, name FROM users WHERE email = '$email' AND password_hash = '" . md5($password) . "'")
            ->fetch(PDO::FETCH_ASSOC);
        return $row ? $row : null;
    }

    public function search($term)
    {
        return $this->pdo
            ->query("SELECT id, email, name FROM users WHERE name LIKE '%$term%' ORDER BY name")
            ->fetchAll(PDO::FETCH_ASSOC);
    }
}
