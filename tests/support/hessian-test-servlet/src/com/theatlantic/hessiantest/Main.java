package com.theatlantic.hessiantest;

import org.eclipse.jetty.server.Server;
import org.eclipse.jetty.server.ServerConnector;
import org.eclipse.jetty.servlet.ServletContextHandler;
import org.eclipse.jetty.servlet.ServletHolder;
import com.caucho.hessian.test.TestHessian2Servlet;

public class Main extends TestHessian2Servlet {

    private static final long serialVersionUID = -3429056066423924965L;

    public static void main(String[] args) throws Exception {
        Server server = new Server(0);
        ServletContextHandler context = new ServletContextHandler(ServletContextHandler.SESSIONS);
        server.setHandler(context);
        ServletHolder servletHolder = new ServletHolder(new Main());
        context.addServlet(servletHolder, "/api");
        server.start();
        int port = ((ServerConnector)server.getConnectors()[0]).getLocalPort();
        System.out.println("Listening on port: " + port);
        server.join();
    }

}

