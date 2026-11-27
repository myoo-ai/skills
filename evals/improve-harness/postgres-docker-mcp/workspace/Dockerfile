FROM golang:1.26 AS build
WORKDIR /src
COPY . .
RUN go build -o /out/ ./cmd/...

FROM gcr.io/distroless/base-debian12
COPY --from=build /out/ /app/
