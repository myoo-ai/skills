# Changelog

## 🚀 ferrylog 2.4.0: A Game-Changing Release!

We're thrilled to announce ferrylog 2.4.0, our most powerful release yet! This update represents a significant leap forward in log shipping, delivering seamless performance improvements and a host of exciting new features that will transform the way you manage your logs.

### ✨ Key Highlights

- **Blazing-Fast Compression:** ferrylog now supports zstd compression, dramatically reducing bandwidth usage and ensuring your logs arrive faster than ever. ([#412](https://github.com/ferrylog/ferrylog/pull/412))
- **Robust Retry Logic:** Failed batches are now retried with exponential backoff, up to 8 attempts, providing unparalleled reliability. ([#398](https://github.com/ferrylog/ferrylog/issues/398))
- **Enhanced Observability:** A brand-new `/metrics` endpoint exposes Prometheus metrics, empowering you to gain deep insights into your pipeline. ([#420](https://github.com/ferrylog/ferrylog/pull/420))

### ⚠️ Breaking Changes

It's important to note that the `batch_size` setting has been renamed to `max_batch_bytes` and is now measured in bytes rather than lines. This change ensures greater consistency and predictability across all environments. To migrate, simply update your configuration file as shown below:

```toml
[output.http]
url = "https://logs.example.com/ingest"
max_batch_bytes = 1048576
compression = "zstd"
```

Configurations that still use `batch_size` will fail to start with a clear and helpful error message, ensuring you never miss a beat.

### 🐛 Bug Fixes

- Fixed a critical issue where log lines longer than 64 KiB were silently truncated, ensuring data integrity across the board. ([#405](https://github.com/ferrylog/ferrylog/issues/405))
- Resolved a memory leak in the file watcher that occurred when more than 1000 files were rotated per hour. ([#409](https://github.com/ferrylog/ferrylog/issues/409))

### 🙏 Thank You

We want to extend our heartfelt gratitude to our amazing community of contributors who made this release possible. Your passion and dedication continue to drive ferrylog forward. Upgrade today with `ferrylog self-update --version 2.4.0` and experience the difference for yourself!

In conclusion, ferrylog 2.4.0 is a testament to our unwavering commitment to building the best log shipping experience available. Happy logging! 🎉
