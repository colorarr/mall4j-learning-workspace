FROM eclipse-temurin:17-jre-jammy

WORKDIR /opt/mall-mcp-server

COPY target/mall-mcp-server-0.0.1-SNAPSHOT.jar app.jar

EXPOSE 18081

ENTRYPOINT ["java", "-Xms128m", "-Xmx384m", "-jar", "/opt/mall-mcp-server/app.jar"]
