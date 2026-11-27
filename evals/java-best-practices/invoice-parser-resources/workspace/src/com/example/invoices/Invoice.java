package com.example.invoices;

import java.util.Date;

public class Invoice {

    private String number;
    private Date issued;
    private long amountCents;

    public Invoice(String number, Date issued, long amountCents) {
        this.number = number;
        this.issued = issued;
        this.amountCents = amountCents;
    }

    public String getNumber() {
        return number;
    }

    public Date getIssued() {
        return issued;
    }

    public long getAmountCents() {
        return amountCents;
    }

    @Override
    public String toString() {
        return "Invoice[" + number + ", " + issued + ", " + amountCents + "]";
    }
}
