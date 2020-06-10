package com.theatlantic.hessiantest;

import java.io.IOException;
import java.net.ServerSocket;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Arrays;
import java.util.Iterator;
import java.util.List;

import org.eclipse.jetty.server.Connector;
import org.eclipse.jetty.server.Handler;
import org.eclipse.jetty.server.HttpConfiguration;
import org.eclipse.jetty.server.HttpConnectionFactory;
import org.eclipse.jetty.server.SecureRequestCustomizer;
import org.eclipse.jetty.server.Server;
import org.eclipse.jetty.server.ServerConnector;
import org.eclipse.jetty.server.SslConnectionFactory;
import org.eclipse.jetty.server.handler.ContextHandlerCollection;
import org.eclipse.jetty.servlet.ServletContextHandler;
import org.eclipse.jetty.servlet.ServletHandler;
import org.eclipse.jetty.servlet.ServletHolder;
import org.eclipse.jetty.util.ssl.SslContextFactory;

import com.caucho.hessian.test.TestHessian2Servlet;
import com.caucho.hessian.test.TestObject;


public class Main extends TestHessian2Servlet {

    private static Server server;
    private static ServletHandler servletHandler;
    private static ServletHolder servletHolder;
    private static ServerConnector httpConnector;
    private static ServerConnector sslConnector;

    private static final long serialVersionUID = -3429056066423924965L;

    public String replyString_emoji() {
        return "\uD83D\uDE03";
    }

    public Object argString_emoji(Object v) {
        if (v.equals(replyString_emoji())) {
            return true;
        }
        return getInputDebug();
    }

    public String replyString_unicodeTwoOctetsCompact() {
        return "\u00E9"; // é
    }

    public Object argString_unicodeTwoOctetsCompact(Object v) {
        if (v.equals(replyString_unicodeTwoOctetsCompact())) {
            return true;
        }
        return getInputDebug();
    }

    public String replyString_unicodeThreeOctetsCompact() {
        return "\u5B57"; // 字
    }

    public Object argString_unicodeThreeOctetsCompact(Object v) {
        if (v.equals(replyString_unicodeThreeOctetsCompact())) {
            return true;
        }
        return getInputDebug();
    }

    public String replyString_unicodeTwoOctets() {
        return String.join("", Collections.nCopies(64, "\u00E9"));  // é
    }

    public Object argString_unicodeTwoOctets(Object v) {
        if (v.equals(replyString_unicodeTwoOctets())) {
            return true;
        }
        return getInputDebug();
    }

    public String replyString_unicodeThreeOctets() {
        return String.join("", Collections.nCopies(64, "\u5B57")); // 字
    }

    public Object argString_unicodeThreeOctets(Object v) {
        if (v.equals(replyString_unicodeThreeOctets())) {
            return true;
        }
        return getInputDebug();
    }

    public Iterator<String> replyUntypedVariableList_0() {
        String items[] = {};
        List<String> list = Arrays.asList(items);
        return list.iterator();
    }

    public Iterator<String> replyUntypedVariableList_1() {
        String items[] = {"a", "b"};
        List<String> list = Arrays.asList(items);
        return list.iterator();
    }

    public Object replyListOfListWithRefs() {
        ArrayList list = new ArrayList();

        TestObject obj = new TestObject(0);
    
        list.add(obj);
        list.add(obj);

        ArrayList listOfLists = new ArrayList();

        listOfLists.add(list);
        listOfLists.add(list);

        return listOfLists;
    }

    public Object argListOfListWithRefs(Object v) {
        if (v.equals(replyListOfListWithRefs())) {
            return true;
        }
        return getInputDebug();
    }

    public String replyString_65536()
    {
      StringBuilder sb = new StringBuilder();

      for (int i = 0; i < 64 * 16; i++) {
        sb.append("" + (i / 100) + (i / 10 % 10) + (i % 10) + " 56789012345678901234567890123456789012345678901234567890123\n");
      }

      sb.setLength(65536);

      return sb.toString();
    }

    public static synchronized int findFreePort() throws IOException {
        try (ServerSocket socket = new ServerSocket(0)) {
            return socket.getLocalPort();
        }
    }

    public static void main(String[] args) throws Exception {
        server = new Server(0);
  
        int httpPort = findFreePort();
        int sslPort = findFreePort();
  
        final ContextHandlerCollection handlerCollection = new ContextHandlerCollection();
  
        final ServletContextHandler contextHandler = new ServletContextHandler(ServletContextHandler.SESSIONS);
        servletHandler = new ServletHandler();
        contextHandler.insertHandler(servletHandler);
  
        handlerCollection.setHandlers(new Handler[]{contextHandler});
  
        server.setHandler(handlerCollection);
  
        httpConnector = new ServerConnector(server);
        httpConnector.setPort(httpPort);
  
        final SslContextFactory sslContextFactory = new SslContextFactory();
  
        sslContextFactory.setKeyStorePath(Main.class.getResource("/hessiantest.jks").toExternalForm());
        sslContextFactory.setKeyStorePassword("password");
        sslContextFactory.setKeyManagerPassword("password");
  
        final HttpConfiguration https = new HttpConfiguration();
        https.addCustomizer(new SecureRequestCustomizer());
        sslConnector = new ServerConnector(server,
                new SslConnectionFactory(sslContextFactory, "http/1.1"),
                new HttpConnectionFactory(https));
        sslConnector.setPort(sslPort);
  
        server.setConnectors(new Connector[]{httpConnector, sslConnector});
  
        servletHolder = servletHandler.addServletWithMapping(Main.class, "/api");
  
        server.start();
        System.out.println("Listening on http port: " + httpPort + ", ssl port: " + sslPort);
        server.join();
    }

}

