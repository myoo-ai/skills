namespace Example.Orders;

public interface IOrderValidator
{
    Task<bool> ValidateAsync(Order order);
}
