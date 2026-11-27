# Pricing

Reads supplier price files, one price line per row (`SKU region quantity unit-price`). `src/Pricing` is the library, used by the price import service that runs in our Amsterdam and Istanbul offices. `src/Pricing.Demo` parses the sample file. Both target `net9.0` and build with the .NET 9 SDK.

```sh
dotnet build src/Pricing.Demo
dotnet run --project src/Pricing.Demo
```
