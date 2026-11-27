namespace Example.Orders;

public sealed class EmailDomainValidator : IOrderValidator
{
    private readonly HashSet<string> _allowedDomains;

    public EmailDomainValidator(IEnumerable<string> allowedDomains)
    {
        _allowedDomains = new HashSet<string>(allowedDomains, StringComparer.OrdinalIgnoreCase);
    }

    public async Task<bool> ValidateAsync(Order order)
    {
        await Task.Delay(10);
        int at = order.Customer.LastIndexOf('@');
        return at > 0 && _allowedDomains.Contains(order.Customer[(at + 1)..]);
    }
}
