name := "kafka-scala-sample"
version := "1.0"
scalaVersion := "2.12.1"

libraryDependencies ++= {
	Seq(
			// Kafka
            "org.apache.kafka" %% "kafka" % "1.0.0",
			// Kafka
			"org.apache.kafka" % "kafka-clients" % "1.0.0",
			// Kafka Stream
            "org.apache.kafka" % "kafka-streams" % "1.0.0"
	   )
}
