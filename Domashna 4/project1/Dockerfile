# Build Stage
FROM maven:3.8.4-openjdk-17-slim AS build

# Set the working directory in the container
WORKDIR /app

# Copy the pom.xml and the project files to the container
COPY pom.xml .
COPY src ./src

# Build the application using Maven
RUN mvn clean package -DskipTests

# Runtime Stage
FROM openjdk:17-jdk-slim

# Set the working directory in the container
WORKDIR /app

# Copy the built JAR file from the previous stage and rename it
COPY --from=build /app/target/project1-0.0.1-SNAPSHOT.jar project1.jar

# Set the command to run the application
CMD ["java", "-jar", "project1.jar"]