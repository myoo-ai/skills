# invoices

Imports supplier invoice files. It has no build tool and targets JDK 25.

```sh
javac -Xlint:all -Werror -d out $(find src -name '*.java')
java -cp out com.example.invoices.Main data/*.txt
```
