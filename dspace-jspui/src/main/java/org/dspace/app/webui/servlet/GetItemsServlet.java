package org.dspace.app.webui.servlet;

import java.io.IOException;
import java.lang.reflect.Field;
import java.net.URL;
import java.net.URLEncoder;
import java.sql.SQLException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Scanner;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.log4j.Logger;
import org.dspace.app.webui.servlet.DSpaceServlet;
import org.dspace.core.Context;
import org.dspace.services.ConfigurationService;
import org.dspace.services.factory.DSpaceServicesFactory;
import org.json.JSONArray;
import org.json.JSONObject;

/**
 *
 * @author pandr
 */
public class GetItemsServlet extends DSpaceServlet {

    /**
     * log4j category
     */
    private static Logger log = Logger.getLogger(GetItemsServlet.class);


    @Override
    protected void doDSGet(Context context, HttpServletRequest request,
            HttpServletResponse response) throws ServletException,
            SQLException,
            IOException {

        try {

            Map<String,String> collections = new HashMap<>();
            collections.put("bf74bbe4-60dc-46a3-bf31-b76335d87ba1", "EUI");
            collections.put("3ab41e89-0aaf-4e8e-a627-e574b1d968c3", "CESSDA");


            String query = request.getParameter("query");
            String lastModified = request.getParameter("lastModified");

            ConfigurationService configurationService = DSpaceServicesFactory.getInstance().getConfigurationService();

            // build the SOLR URL
            String stringURL = configurationService.getProperty("solr.server") + "/search/select?q=" + URLEncoder.encode(query + " AND lastModified:[" + lastModified + "T00\\:00\\:00Z TO *]", "UTF-8") + "&rows=100000&fl=handle,location.coll&wt=json";

            URL url = new URL(stringURL);
         
            // read from the SOLR URL
            Scanner scanner = new Scanner(url.openStream());
            String str = new String();
            while (scanner.hasNext())
                str += scanner.nextLine();
            scanner.close();
         
            // build a JSON object containing SOLR data
            JSONObject initialTopLevelJSONObject = new JSONObject(str);
    
            // JSON array containing SOLR docs data
            JSONArray initialDocsJSONArray = initialTopLevelJSONObject.getJSONObject("response").getJSONArray("docs");
    
            // create new JSON objects to contain response data
            JSONObject finalTopLevelJSONObject = new JSONObject();
            JSONObject finalResponseHeaderJSONObject = new JSONObject();
            JSONObject finalResponseJSONObject = new JSONObject();
    
            // create new JSON array to contain response handles data
            JSONArray finalHandlesJSONArray = new JSONArray();
    
            finalResponseHeaderJSONObject.put("query", query);
            finalResponseHeaderJSONObject.put("lastModified", lastModified);
    
            for (int i = 0; i < initialDocsJSONArray.length(); i++) {
                JSONObject finalHandleJSONObject = new JSONObject();
                finalHandleJSONObject.put("handle", initialDocsJSONArray.getJSONObject(i).getString("handle"));
                JSONArray collArray = (JSONArray) initialDocsJSONArray.getJSONObject(i).getJSONArray("location.coll");
                finalHandleJSONObject.put("collection", collections.get(collArray.getString(0)));
                finalHandlesJSONArray.put(finalHandleJSONObject);
            }
    
            finalResponseJSONObject.put("handles", finalHandlesJSONArray);

            // Make finalTopLevelJSONObject ordered
            Field changeMap = finalTopLevelJSONObject.getClass().getDeclaredField("map");
            changeMap.setAccessible(true);
            changeMap.set(finalTopLevelJSONObject, new LinkedHashMap<>());
            changeMap.setAccessible(false);

            finalTopLevelJSONObject.put("responseHeader", finalResponseHeaderJSONObject);

            finalTopLevelJSONObject.put("response", finalResponseJSONObject);

            response.setContentType("application/json; charset=UTF-8");
            response.getWriter().write(finalTopLevelJSONObject.toString());
    
        } catch (Exception e) {
            e.printStackTrace();
        }

    }

    @Override
    protected void doDSPost(Context context, HttpServletRequest request,
            HttpServletResponse response) throws ServletException, IOException,
            SQLException {

        doDSGet(context, request, response);

    }

}