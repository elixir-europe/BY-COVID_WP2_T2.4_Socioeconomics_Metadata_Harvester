package org.dspace.app.webui.servlet;

import java.io.IOException;
import java.sql.SQLException;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.log4j.Logger;
import org.dspace.app.webui.servlet.DSpaceServlet;
import org.dspace.content.Item;
import org.dspace.content.factory.ContentServiceFactory;
import org.dspace.content.service.ItemService;
import org.dspace.core.Context;
import org.dspace.handle.factory.HandleServiceFactory;
import org.dspace.handle.service.HandleService;
import org.dspace.harvest.HarvestedCollection;
import org.dspace.harvest.HarvestedItem;
import org.dspace.harvest.factory.HarvestServiceFactory;
import org.dspace.harvest.service.HarvestedCollectionService;
import org.dspace.harvest.service.HarvestedItemService;
import org.json.JSONArray;
import org.json.JSONObject;

public class GetItemServlet extends DSpaceServlet {

    /**
     * log4j category
     */
    private static Logger log = Logger.getLogger(GetItemServlet.class);


    @Override
    protected void doDSGet(Context context, HttpServletRequest request, HttpServletResponse response)
        throws ServletException, SQLException, IOException {

        try {

            String handle = request.getParameter("handle");

            HandleService handleService = HandleServiceFactory.getInstance().getHandleService();
            ItemService itemService = ContentServiceFactory.getInstance().getItemService();
            HarvestedItemService harvestedItemService = HarvestServiceFactory.getInstance().getHarvestedItemService();
            HarvestedCollectionService harvestedCollectionmService = HarvestServiceFactory.getInstance().getHarvestedCollectionService();

            Item item = itemService.find(context, handleService.resolveToObject(context, handle).getID());

            HarvestedItem harvestedItem = harvestedItemService.find(context, item);
            String oaiID = harvestedItem.getOaiID();
            HarvestedCollection harvestedCollection = harvestedCollectionmService.find(context, item.getOwningCollection());
            String oaiSource = harvestedCollection.getOaiSource();

            String originalOAI = oaiSource + "?verb=GetRecord&metadataPrefix=oai_dc&identifier=" + oaiID;


            JSONArray json = new JSONArray();

            JSONObject jsonPair = new JSONObject();
            jsonPair.put("handle", handle);
            jsonPair.put("oaiSource", originalOAI);
            json.put(jsonPair);

            response.setContentType("application/json; charset=UTF-8");
            response.getWriter().write(json.toString());

        } catch (Exception e) {
            e.printStackTrace();
        }

    }

    @Override
    protected void doDSPost(Context context, HttpServletRequest request, HttpServletResponse response)
        throws ServletException, IOException, SQLException {

        doDSGet(context, request, response);

    }

}

