# Exports

Writes stock exports as CSV files that the warehouse system picks up. `src/Exports` is the library, used by the nightly export job and by the download endpoints of our ASP.NET Core API. `src/Exports.Demo` writes a sample export. Both target `net9.0` and build with the .NET 9 SDK.

```sh
dotnet build src/Exports.Demo
dotnet run --project src/Exports.Demo
```
