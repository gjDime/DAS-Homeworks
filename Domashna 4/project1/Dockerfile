# Stage 1: Build
FROM maven:3.8.4-openjdk-17-slim AS build

WORKDIR /app

COPY pom.xml .
COPY src ./src

RUN mvn clean package -DskipTests

# Stage 2: Run
FROM openjdk:17-jdk-slim

WORKDIR /app

COPY --from=build /app/target/project1-0.0.1-SNAPSHOT.jar app.jar
COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

# Only keep one CMD instruction
CMD ["/wait-for-it.sh", "postgres:5432", "--", "java", "-jar", "app.jar"]