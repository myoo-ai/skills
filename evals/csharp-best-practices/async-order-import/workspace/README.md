# OrderImport

Imports supplier order exports (CSV). `src/OrderImport` is the library, used by the orders API and the desktop back-office tool. `src/OrderImport.Demo` imports the sample file. Both target `net9.0` and build with the .NET 9 SDK.

```sh
dotnet build src/OrderImport.Demo
dotnet run --project src/OrderImport.Demo
```
