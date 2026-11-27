# prices

Nightly price refresh against the supplier API. It has no build tool and targets JDK 25.

```sh
javac -Xlint:all -Werror -d out $(find src -name '*.java')
java -cp out com.example.prices.Main
```
